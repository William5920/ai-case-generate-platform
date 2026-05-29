# AI 原生过程证明

> 本文档记录了智能测试用例平台在 AI 辅助开发过程中，由 AI 做出的关键技术决策、问题诊断思路和架构选择。每一节对应一个独立的问题域，包含"问题 → 诊断 → 方案 → 验证"的完整决策链路。

---

## 目录

- [1. 需求标准化模块后端架构设计](#1-需求标准化模块后端架构设计)
- [2. 需求探索功能：文件上传 vs 文本录入的上下文理解缺陷](#2-需求探索功能文件上传-vs-文本录入的上下文理解缺陷)
- [3. 导出接口编码链路修复](#3-导出接口编码链路修复)
- [4. AI 调整 v2.3 特性实现](#4-ai-调整-v23-特性实现)
- [5. 需求拆分"手动添加"端点缺失](#5-需求拆分手动添加端点缺失)
- [6. 需求创建 inputMode 校验过严导致 422](#6-需求创建-inputmode-校验过严导致-422)
- [7. 决策模式总结](#7-决策模式总结)

---

## 1. 需求标准化模块后端架构设计

### 背景

基于 API 接口文档（`docs/api/standardization.md`）和产品需求文档（`docs/prd/requirements_standardization_module.md`），从零构建需求标准化模块的完整后端。

### 关键决策

| 决策点 | 方案 | 理由 |
|--------|------|------|
| 分层架构 | schemas / services / routers 三层分离 | 遵循项目现有结构，保持一致性 |
| LLM 容错 | 所有 LLM 调用加 try/except + fallback 内容 | 线上环境 API Key 可能未配置，不能因 LLM 不可用导致整个接口 500 |
| 文件解析 | 独立 `file_service` 支持 docx/xlsx/pdf/md | 前端上传的需求文档格式多样，需统一解析为纯文本供 LLM 消费 |
| Prompt 管理 | 集中到 `agents/prompts.py` | 便于调优和版本管理，避免散落各处 |
| 数据落库时机 | explore_data 实时更新到 requirement JSON 字段 | 避免前端刷新丢失探索进度 |

### 模块文件清单

---

## 2. 需求探索功能：文件上传 vs 文本录入的上下文理解缺陷

### 问题

用户反馈：通过文档上传创建需求后，AI 在探索阶段提出的问题没有体现对上传文档内容的理解；而文本录入方式则能正常理解。

### 诊断过程

1. 检查 `explore_service.start_explore` — 发现文件解析仅在请求参数 `file_id` 有值时执行，但 **未使用 `requirement.file_id` 兜底**
2. 检查前端调用链路 — 前端先上传文件创建需求（file_id 存入 requirement），再调用 `/explore/start` 时可能只传 `requirementId`，不带 `fileId`
3. 结论：文件从未被解析，`raw_content` 为空字符串传入 LLM prompt，AI 只能看到空白的"用户原始需求"

### 修复方案

```python
# explore_service.py - start_explore()
# 修复前：
if file_id and not raw_content:
    raw_content = await file_service.parse_file_content(db, file_id)

# 修复后：
effective_file_id = file_id or requirement.file_id       # ← 关键：从 requirement 对象兜底
if effective_file_id and not raw_content and not requirement.raw_content:
    try:
        raw_content = await file_service.parse_file_content(db, effective_file_id)
        if raw_content:
            requirement.raw_content = raw_content
    except Exception as e:
        logger.warning(f"文件解析失败: {e}")
```

同样的兜底逻辑也在 `send_explore_message` 中补上。

### 决策依据

不修改前端调用方式（代价高），而是在后端做防御性兜底。这遵循"后端应对前端数据不完整有容错能力"的原则。

---

## 3. 导出接口编码链路修复

### 问题演进

| 阶段 | 现象 | 诊断 |
|------|------|------|
| 第1次 | `latin-1 codec can't encode characters in position 21-34` | `Response(content=bytes)` 在 Starlette 内部渲染链路中对非纯 ASCII bytes 走了 `latin-1` 编码 |
| 第2次 | 改为 `Response` + `json.dumps` 后仍报 latin-1 错误 | `standardizedContent` 是 Python dict 对象而非字符串，`.encode()` 前需类型判断 |
| 第3次 | Word 导出内容为 `[object Object]` | 同上，dict 直接转字符串显示为 JS 的 `[object Object]` |

### 最终方案

```python
# 三层防御
raw = data.get("standardizedContent") or data.get("rawContent") or ""
if isinstance(raw, (dict, list)):
    content = json.dumps(raw, ensure_ascii=False, indent=2)   # dict → JSON 字符串
elif isinstance(raw, str):
    content = raw
else:
    content = str(raw)

content_bytes = content.encode("utf-8")
stream = io.BytesIO(content_bytes)

# 使用 StreamingResponse 绕过 Starlette 内部编码转换
return StreamingResponse(
    stream,
    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}.docx"}
)
```

### 关键洞察

1. FastAPI 的 `Response(content=bytes)` 不适合包含中文的二进制流输出 — 应使用 `StreamingResponse`
2. `Content-Disposition` 中文文件名必须使用 RFC 5987 编码：`filename*=UTF-8''{url_encoded_name}`
3. 数据库中存储的字段类型不可假设 — 需要运行时类型判断

---

## 4. AI 调整 v2.3 特性实现

### 需求来源

`docs/api/test-design.md` v2.3 版本新增 4 项变更：
1. 新增 5.5 采纳AI调整建议接口
2. 新增 5.6 拒绝AI调整建议接口
3. 5.2 响应新增 `changeSummary` 字段
4. 5.2 `pendingMindMapData` 字段语义更新

### 设计与实现

#### 数据模型扩展

`AIMessage` 表新增 5 个字段：

| 字段 | 类型 | 用途 |
|------|------|------|
| `msg_type` | VARCHAR(20) | `text` / `proposal`，区分普通消息和提案消息 |
| `change_summary` | TEXT | 提案类型消息的变更摘要 |
| `pending_mindmap_data` | JSON | 提案时的脑图快照，供前端预览 |
| `adopted` | BOOLEAN | 该提案是否已被采纳 |
| `rejected` | BOOLEAN | 该提案是否已被拒绝 |

#### 提案检测策略

不做结构化 JSON 输出（不可靠），改用启发式检测：

```python
if isinstance(ai_content, str) and "调整建议" in ai_content:
    msg_type = "proposal"
    change_summary = self._extract_change_summary(ai_content)
    pending_data = await self._build_pending_mindmap_data(db, session_id)
```

`change_summary` 提取策略：优先查找"变更摘要/调整摘要/变更内容"开头的行 → 取首行（≤120字符）→ 截断。

#### 采纳/拒绝幂等性

```python
# adopt: 标记 adopted=True，如果 pending_mindmap_data 存在则应用变更
msg.adopted = True
msg.rejected = False

# reject: 仅标记，不做数据变更
msg.rejected = True
msg.adopted = False
```

### 新增路由

---

## 5. 需求拆分"手动添加"端点缺失

### 问题

前端调用 `POST /api/v1/requirements/req-xxx/splits` 返回 404。

### 诊断

- 前端 `/splits`（复数，REST 语义："拆分项集合"）
- 后端只有 `/split`（单数，语义："执行拆分"）
- 路由不匹配

### 修复

新增 `POST /{requirement_id}/splits` 端点，调用已有的 `split_service.add_split()`。注意保持 `/split` 和 `/splits` 两个端点共存（语义不同）。

---

## 6. 需求创建 inputMode 校验过严导致 422

### 问题

`POST /api/v1/explore/start` → 创建需求时报错：`ValueError: 文档上传模式下 fileId 不能为空`

### 诊断

1. 前端 `inputMode` 可能传 `"file"` 或 `"document"`（前端有两个不同取值）
2. `explore_router` 在无 `requirementId` 时自动创建需求，但 `fileId` 可能为空
3. `requirement_service.create_requirement` 对 `inputMode == "file"` 且无 `fileId` 直接抛异常

### 修复

两处改为**静默降级**而非抛异常：

```python
# requirement_service.py
if data.inputMode in ("file", "document") and not data.fileId:
    data.inputMode = "text"  # 降级为文本模式，而非报错

# explore_router.py
input_mode = req.inputMode or "text"
if input_mode in ("file", "document") and not req.fileId:
    input_mode = "text"
```

### 决策依据

前端可能因各种边界条件未传 `fileId`，后端不应因此阻断用户流程。降级到文本模式让用户至少能继续操作，比直接 400/422 更友好。

---

## 7. 决策模式总结

### 反复出现的模式

| 模式 | 出现次数 | 示例 |
|------|----------|------|
| **防御性兜底** | 5+ | 文件解析、inputMode 降级、LLM fallback、类型判断 |
| **前端不修改，后端适配** | 4+ | 路由匹配（splits/split）、字段取值兼容（file/document）、响应格式对齐 |
| **try/except 包裹外部依赖** | 3+ | LLM 调用、文件解析、数据库操作 |
| **运行时类型判断** | 2+ | standardizedContent 可能是 dict/str/None |

### 核心原则

1. **后端应对前端数据不完整具备容错能力** — 不假设前端总是传全所有字段
2. **外部依赖不可信** — LLM API、文件系统都需 fallback
3. **降级优于报错** — 用户流程不应因非关键数据缺失而中断
4. **先诊断再修复** — 读代码定位根因（而非表象），再做最小改动

---

## 附录：接口端点全景

### 需求标准化模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/requirements` | 创建需求 |
| GET | `/api/v1/requirements` | 需求列表 |
| GET | `/api/v1/requirements/{id}` | 需求详情 |
| PUT | `/api/v1/requirements/{id}` | 更新需求 |
| DELETE | `/api/v1/requirements/{id}` | 删除需求 |
| GET | `/api/v1/requirements/{id}/export` | 导出需求文档 |
| POST | `/api/v1/requirements/{id}/split` | 执行需求拆分 |
| POST | `/api/v1/requirements/{id}/splits` | 手动添加拆分项 |
| POST | `/api/v1/requirements/{id}/confirm-and-test` | 确认拆分并生成测试 |
| POST | `/api/v1/explore/start` | 开始需求探索 |
| POST | `/api/v1/explore/chat` | 发送探索消息 |
| POST | `/api/v1/standardize` | 标准化需求 |
| GET | `/api/v1/standardize/{id}` | 获取标准化结果 |
| POST | `/api/v1/standardize/quality` | 质量评分 |
| POST | `/api/v1/standardize/chat/{id}/confirm` | 确认调整建议 |
| POST | `/api/v1/standardize/chat/{id}/reject` | 拒绝调整建议 |
| POST | `/api/v1/standardize/versions/{id}/restore` | 恢复历史版本 |
| GET | `/api/v1/standardize/versions/{id}` | 获取版本列表 |

### 测试设计模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/test-design/requirements` | 导入需求 |
| GET | `/api/v1/test-design/requirements` | 需求列表 |
| GET | `/api/v1/test-design/requirements/{id}/mindmap` | 获取脑图数据 |
| POST | `/api/v1/test-design/ai-adjust/sessions` | 发起 AI 调整对话 |
| POST | `/api/v1/test-design/ai-adjust/sessions/{id}/messages` | 发送对话消息 |
| GET | `/api/v1/test-design/ai-adjust/sessions/{id}/messages` | 获取对话历史 |
| POST | `/api/v1/test-design/ai-adjust/sessions/{id}/apply` | 应用 AI 调整 |
| POST | `/api/v1/test-design/ai-adjust/sessions/{id}/messages/{mid}/adopt` | 采纳 AI 调整建议 (v2.3) |
| POST | `/api/v1/test-design/ai-adjust/sessions/{id}/messages/{mid}/reject` | 拒绝 AI 调整建议 (v2.3) |