# 需求标准化模块 - 后端开发规划文档

## 1. 模块概述

### 1.1 模块定位
需求标准化模块是智能测试用例平台的核心入口模块，负责将用户输入的原始需求（文本或文档）通过AI先进行需求探索与理解，再转换为标准化的需求规格说明书，并拆分为可执行的单个需求项，为后续测试设计提供结构化输入。

### 1.2 核心流程

```
需求录入 → AI需求探索 → 文档生成 → 文档编辑调整 → 需求拆分 → 进入测试设计
```

### 1.3 核心目标
- 实现需求CRUD与文件上传，支持文本/文档两种输入模式
- 实现模板管理，支持SRS和User-Story两种预设模板及AI推荐
- 实现AI需求探索，通过结构化提问与用户对话收集需求信息
- 实现文档标准化，基于探索数据生成标准化文档
- 实现AI文档调整，支持多轮对话调整文档内容，采纳/拒绝AI建议
- 实现版本管理，记录文档变更历史，支持版本对比和恢复
- 实现质量评分，自动评估标准化文档质量
- 实现需求拆分，将标准化文档拆分为可执行的单个需求项
- 实现文档导出（Markdown/Word）和知识库上传
- 实现历史记录管理

---

## 2. 技术方案

### 2.1 技术选型

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109.x | Web框架 |
| SQLAlchemy | 2.0.x | ORM框架，数据库操作 |
| SQLite | - | 轻量级数据库（可迁移MySQL） |
| Pydantic | 2.5.x | 请求/响应数据模型 |
| python-docx | 1.x | docx文件解析 |
| openpyxl | 3.x | xlsx文件解析 |
| python-multipart | 0.0.x | 文件上传处理 |
| OpenAI API | 1.x | 大模型调用（标准化、探索、拆分等） |

### 2.2 统一响应格式

与现有认证模块保持一致：

```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {},
  "traceId": "uuid-string"
}
```

### 2.3 认证机制
所有接口（除公开接口外）需携带 `Authorization: Bearer <token>` 请求头，通过 `get_current_user` 依赖注入获取当前用户，实现数据隔离。

---

## 3. 数据库设计

### 3.1 requirements 表（扩展现有表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(64) | PK | 主键，格式：req-{uuid8} |
| user_id | VARCHAR(64) | NOT NULL | 关联用户ID |
| title | VARCHAR(255) | NOT NULL | 需求标题 |
| input_mode | VARCHAR(10) | NOT NULL | 输入模式：text/file |
| raw_content | TEXT | | 原始需求文本内容 |
| file_id | VARCHAR(64) | FK -> uploaded_files.id | 关联上传文件ID |
| template_id | VARCHAR(20) | DEFAULT 'user-story' | 需求文档模板ID |
| standardized_content | TEXT | | 标准化后的文档内容（Markdown） |
| explore_data | JSON | | AI需求探索收集的数据 |
| status | VARCHAR(20) | DEFAULT 'draft' | 状态：draft/exploring/standardized/splitted |
| quality_score | INTEGER | | 质量评分（0-100） |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.2 uploaded_files 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(64) | PK | 主键，格式：file-{uuid8} |
| user_id | VARCHAR(64) | NOT NULL | 关联用户ID |
| original_filename | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_path | VARCHAR(500) | NOT NULL | 存储路径 |
| file_size | INTEGER | NOT NULL | 文件大小（字节） |
| file_type | VARCHAR(100) | | 文件MIME类型 |
| purpose | VARCHAR(20) | NOT NULL | 用途：requirement/knowledge |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.3 explore_messages 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(64) | PK | 主键，格式：em-{uuid8} |
| requirement_id | VARCHAR(64) | FK -> requirements.id | 关联需求 |
| role | VARCHAR(10) | NOT NULL | 角色：user/assistant |
| content | TEXT | NOT NULL | 消息内容 |
| dimension_key | VARCHAR(50) | | 探索维度标识 |
| dimension_label | VARCHAR(50) | | 探索维度名称 |
| quick_replies | JSON | | 快捷回复选项 |
| replied | BOOLEAN | DEFAULT FALSE | 是否已回复 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.4 adjust_messages 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(64) | PK | 主键，格式：am-{uuid8} |
| requirement_id | VARCHAR(64) | FK -> requirements.id | 关联需求 |
| role | VARCHAR(10) | NOT NULL | 角色：user/assistant |
| content | TEXT | NOT NULL | 消息内容 |
| message_type | VARCHAR(20) | DEFAULT 'discussion' | 消息类型：proposal/discussion |
| proposal_content | TEXT | | AI建议的文档内容变更 |
| change_summary | TEXT | | 变更摘要 |
| confirmed | BOOLEAN | DEFAULT FALSE | 是否已采纳 |
| rejected | BOOLEAN | DEFAULT FALSE | 是否已拒绝 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.5 doc_versions 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(64) | PK | 主键，格式：ver-{uuid8} |
| requirement_id | VARCHAR(64) | FK -> requirements.id | 关联需求 |
| version_number | INTEGER | NOT NULL | 版本号 |
| content | TEXT | NOT NULL | 版本文档内容 |
| description | VARCHAR(255) | | 版本描述 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.6 split_requirements 表（扩展现有表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | VARCHAR(64) | PK | 主键，格式：split-{uuid8} |
| requirement_id | VARCHAR(64) | FK -> requirements.id | 关联需求 |
| content | TEXT | NOT NULL | 拆分项内容 |
| order_index | INTEGER | NOT NULL | 排序序号 |
| status | VARCHAR(20) | DEFAULT 'pending' | 状态：pending/confirmed |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.7 实体关系

```
users 1──N requirements
users 1──N uploaded_files

requirements 1──1 uploaded_files (file_id, 可选)
requirements 1──N explore_messages
requirements 1──N adjust_messages
requirements 1──N doc_versions
requirements 1──N split_requirements
```

---

## 4. API 接口设计

### 4.1 接口总览

| 模块 | 接口 | 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|------|------|
| 需求管理 | 创建需求 | POST | /api/v1/requirements | 是 | 创建需求记录 |
| | 获取需求列表 | GET | /api/v1/requirements | 是 | 分页、搜索、状态筛选 |
| | 获取需求详情 | GET | /api/v1/requirements/{id} | 是 | 含标准化文档和拆分结果 |
| | 更新需求 | PUT | /api/v1/requirements/{id} | 是 | 更新需求信息 |
| | 删除需求 | DELETE | /api/v1/requirements/{id} | 是 | 级联删除关联数据 |
| 文件上传 | 上传需求文档 | POST | /api/v1/upload | 是 | multipart/form-data |
| 模板管理 | 获取模板列表 | GET | /api/v1/templates | 否 | 返回预设模板 |
| | 获取模板详情 | GET | /api/v1/templates/{id} | 否 | 返回模板完整信息 |
| | AI推荐模板 | POST | /api/v1/templates/recommend | 是 | 基于内容推荐模板 |
| AI需求探索 | 启动需求探索 | POST | /api/v1/explore/start | 是 | 初始化探索会话 |
| | 发送探索消息 | POST | /api/v1/explore/chat | 是 | 发送对话消息 |
| | 获取探索对话历史 | GET | /api/v1/explore/{requirementId}/messages | 是 | 获取对话记录 |
| | 获取探索状态 | GET | /api/v1/explore/status | 是 | 获取理解度等状态 |
| 文档标准化 | 执行标准化 | POST | /api/v1/standardize | 是 | 生成标准化文档 |
| | 获取标准化结果 | GET | /api/v1/standardize/{requirementId} | 是 | 获取标准化文档 |
| AI文档调整 | 发送调整消息 | POST | /api/v1/standardize/chat | 是 | AI对话调整文档 |
| | 获取调整对话历史 | GET | /api/v1/standardize/chat/{requirementId}/messages | 是 | 获取调整对话记录 |
| | 采纳AI建议 | POST | /api/v1/standardize/adopt | 是 | 采纳建议更新文档 |
| | 拒绝AI建议 | POST | /api/v1/standardize/reject | 是 | 拒绝建议 |
| 版本管理 | 获取版本列表 | GET | /api/v1/requirements/{id}/versions | 是 | 获取文档版本列表 |
| | 获取版本详情 | GET | /api/v1/versions/{versionId} | 是 | 获取特定版本内容 |
| | 恢复版本 | POST | /api/v1/versions/{versionId}/restore | 是 | 恢复到指定版本 |
| | 获取版本差异 | GET | /api/v1/versions/{versionId}/diff | 是 | 对比两个版本差异 |
| 质量评分 | 执行质量评分 | POST | /api/v1/requirements/{id}/quality-score | 是 | 评估文档质量 |
| 需求拆分 | 执行需求拆分 | POST | /api/v1/requirements/{id}/split | 是 | AI拆分标准化文档 |
| | 获取拆分结果列表 | GET | /api/v1/requirements/{id}/splits | 是 | 获取拆分项列表 |
| | 更新拆分项 | PUT | /api/v1/splits/{splitId} | 是 | 更新拆分项内容 |
| | 删除拆分项 | DELETE | /api/v1/splits/{splitId} | 是 | 删除拆分项 |
| | 手动添加拆分项 | POST | /api/v1/requirements/{id}/splits | 是 | 手动添加拆分项 |
| | 确认并进入测试设计 | POST | /api/v1/requirements/{id}/confirm-split | 是 | 确认拆分结果 |
| 文档导出 | 导出标准化文档 | GET | /api/v1/requirements/{id}/export | 是 | 导出Markdown/Word |
| 知识库上传 | 上传文档至知识库 | POST | /api/v1/knowledge-base/upload-doc | 是 | 上传标准化文档到知识库 |
| 历史记录 | 获取历史记录列表 | GET | /api/v1/history | 是 | 获取用户历史记录 |
| | 获取历史记录详情 | GET | /api/v1/history/{id} | 是 | 获取历史记录详情 |

### 4.2 核心接口详细设计

#### POST /api/v1/requirements

**请求体：**
```json
{
  "title": "用户登录系统需求",
  "inputMode": "text",
  "rawContent": "实现用户登录功能...",
  "templateId": "srs"
}
```

**成功响应（200）：**
```json
{
  "success": true,
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "req-abc12345",
    "title": "用户登录系统需求",
    "inputMode": "text",
    "rawContent": "实现用户登录功能...",
    "templateId": "srs",
    "status": "draft",
    "createdAt": "2026-05-25T10:00:00.000Z",
    "updatedAt": "2026-05-25T10:00:00.000Z"
  }
}
```

#### POST /api/v1/explore/start

**请求体：**
```json
{
  "requirementId": "req-abc12345",
  "templateId": "srs"
}
```

**成功响应：** 返回AI首条消息，包含对需求的理解和第一个维度的提问。

#### POST /api/v1/explore/chat

**请求体：**
```json
{
  "requirementId": "req-abc12345",
  "content": "需要支持微信登录，会话保持2小时",
  "dimensionKey": "functional"
}
```

**成功响应：** 返回AI回复，包含下一个维度的提问或生成建议。

#### POST /api/v1/standardize

**请求体：**
```json
{
  "requirementId": "req-abc12345",
  "templateId": "srs",
  "exploreData": [
    {"dimensionKey": "purpose", "content": "..."},
    {"dimensionKey": "functional", "content": "..."}
  ]
}
```

**成功响应：** 返回生成的标准化文档内容。

#### POST /api/v1/standardize/chat

**请求体：**
```json
{
  "requirementId": "req-abc12345",
  "content": "我想调整性能指标"
}
```

**成功响应：** 返回AI建议（proposal类型），包含建议内容。

#### POST /api/v1/standardize/adopt

**请求体：**
```json
{
  "messageId": "am-xyz12345",
  "requirementId": "req-abc12345"
}
```

#### POST /api/v1/requirements/{id}/split

**请求体：**
```json
{
  "standardizedContent": "# 用户登录系统需求规格说明书\n..."
}
```

**成功响应：** 返回拆分后的需求列表。

---

## 5. 项目文件结构

```
backend/app/
├── core/
│   ├── config.py                  # 修改: 新增上传目录、AI相关配置
│   ├── database.py                # 不变
│   ├── dependencies.py            # 不变
│   ├── security.py                # 不变
│   └── response.py                # 新增: 统一响应格式封装
├── models/
│   ├── user.py                    # 不变
│   ├── db_models.py               # 修改: 扩展Requirement、SplitRequirement模型
│   ├── requirement.py             # 新增: 需求标准化相关ORM模型
│   └── ...
├── schemas/
│   ├── auth.py                    # 不变
│   ├── requirement.py             # 新增: 需求管理请求/响应模型
│   ├── template.py                # 新增: 模板相关模型
│   ├── explore.py                 # 新增: AI探索相关模型
│   ├── standardize.py             # 新增: 标准化相关模型
│   ├── version.py                 # 新增: 版本管理模型
│   └── split.py                   # 新增: 需求拆分模型
├── routers/
│   ├── auth.py                    # 不变
│   ├── requirement.py             # 新增: 需求管理路由
│   ├── template.py                # 新增: 模板管理路由
│   ├── explore.py                 # 新增: AI需求探索路由
│   ├── standardize.py             # 新增: 文档标准化路由
│   ├── version.py                 # 新增: 版本管理路由
│   ├── split.py                   # 新增: 需求拆分路由
│   └── ...
├── services/
│   ├── auth_service.py            # 不变
│   ├── requirement_service.py     # 新增: 需求管理业务逻辑
│   ├── template_service.py        # 新增: 模板管理业务逻辑
│   ├── explore_service.py         # 新增: AI需求探索业务逻辑
│   ├── standardize_service.py     # 新增: 文档标准化业务逻辑
│   ├── version_service.py         # 新增: 版本管理业务逻辑
│   ├── split_service.py           # 新增: 需求拆分业务逻辑
│   ├── file_service.py            # 新增: 文件上传/解析业务逻辑
│   ├── export_service.py          # 新增: 文档导出业务逻辑
│   └── ...
├── ai/
│   ├── __init__.py
│   ├── llm_client.py              # 新增: 大模型客户端封装
│   └── prompts/
│       ├── __init__.py
│       ├── explore.py             # 新增: 需求探索Prompt模板
│       ├── standardize.py         # 新增: 标准化生成Prompt模板
│       ├── adjust.py              # 新增: 文档调整Prompt模板
│       └── split.py               # 新增: 需求拆分Prompt模板
└── main.py                        # 修改: 注册新路由
```

---

## 6. 核心模块设计

### 6.1 response.py — 统一响应格式

```python
def success_response(message: str, data=None, trace_id: str = None) -> dict:
    return {
        "success": True,
        "code": 200,
        "message": message,
        "data": data,
        "traceId": trace_id or str(uuid.uuid4())
    }

def error_response(code: int, message: str, trace_id: str = None) -> dict:
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": None,
        "traceId": trace_id or str(uuid.uuid4())
    }
```

### 6.2 requirement.py (model) — 需求ORM模型

扩展现有的Requirement模型，新增字段：
- `input_mode` — 输入模式
- `file_id` — 关联文件
- `template_id` — 模板ID
- `standardized_content` — 标准化文档
- `explore_data` — 探索数据（JSON）
- `quality_score` — 质量评分

新增模型：
- `UploadedFile` — 上传文件
- `ExploreMessage` — 探索对话消息
- `AdjustMessage` — 调整对话消息
- `DocVersion` — 文档版本

### 6.3 template_service.py — 模板管理

- `get_template_list()` — 返回预设模板列表（SRS + User-Story）
- `get_template_detail(template_id)` — 返回模板详情（含维度和章节结构）
- `recommend_template(content)` — 基于内容关键词推荐模板

模板数据结构与前端 `requirementTemplate.js` 保持一致。

### 6.4 explore_service.py — AI需求探索

- `start_explore(requirement_id, template_id)` — 初始化探索会话，生成AI首条消息
- `send_explore_message(requirement_id, content, dimension_key)` — 处理用户回复，生成AI下一维度提问
- `get_explore_messages(requirement_id)` — 获取探索对话历史
- `get_explore_status(requirement_id)` — 获取探索状态（理解度、已探索维度等）

**AI交互流程：**
1. 根据模板维度列表，逐个维度向用户提问
2. 记录用户的回答到explore_data
3. 计算需求理解度 = 已覆盖维度数 / 总维度数
4. 理解度≥80%时，AI主动提示可以生成文档

### 6.5 standardize_service.py — 文档标准化

- `process_standardize(requirement_id, template_id, explore_data)` — 基于探索数据生成标准化文档
- `get_standardized_result(requirement_id)` — 获取标准化文档
- `send_adjust_message(requirement_id, content)` — AI对话调整文档
- `adopt_proposal(message_id, requirement_id)` — 采纳AI建议，更新文档
- `reject_proposal(message_id)` — 拒绝AI建议

**AI生成文档流程：**
1. 将原始需求 + 探索数据 + 模板结构组装为Prompt
2. 调用LLM生成标准化文档（Markdown格式）
3. 保存文档内容，创建初始版本记录
4. 更新需求状态为 `standardized`

**AI调整文档流程：**
1. 用户发送调整请求
2. AI分析请求，生成调整建议（proposal类型消息）
3. 用户采纳：将建议内容合并到文档，创建新版本
4. 用户拒绝：标记建议为已拒绝

### 6.6 version_service.py — 版本管理

- `get_version_list(requirement_id)` — 获取版本列表
- `get_version_detail(version_id)` — 获取版本详情
- `restore_version(version_id, requirement_id)` — 恢复到指定版本
- `get_version_diff(version_id, target_version_id)` — 获取版本差异

### 6.7 split_service.py — 需求拆分

- `execute_split(requirement_id, standardized_content)` — AI拆分标准化文档
- `get_split_list(requirement_id)` — 获取拆分结果列表
- `update_split_item(split_id, content)` — 更新拆分项
- `delete_split_item(split_id)` — 删除拆分项
- `add_split_item(requirement_id, content)` — 手动添加拆分项
- `confirm_split(requirement_id)` — 确认拆分，更新状态为splitted

**AI拆分流程：**
1. 将标准化文档发送给LLM
2. LLM按功能模块/用户故事拆分为独立需求项
3. 保存拆分结果，按order_index排序

### 6.8 file_service.py — 文件上传/解析

- `upload_file(user_id, file, purpose)` — 保存上传文件，返回文件信息
- `parse_file_content(file_id)` — 解析文件内容（docx/xlsx/pdf/md）
- `get_file_info(file_id)` — 获取文件信息

**文件解析支持：**
- `.docx` — 使用python-docx提取文本
- `.xlsx` — 使用openpyxl提取表格内容
- `.pdf` — 使用PyPDF2提取文本
- `.md` — 直接读取文本内容

### 6.9 export_service.py — 文档导出

- `export_markdown(requirement_id)` — 导出Markdown文件
- `export_docx(requirement_id)` — 导出Word文件

### 6.10 llm_client.py — 大模型客户端

```python
class LLMClient:
    def __init__(self, api_key, base_url, model):
        ...

    async def chat(self, messages: list, temperature: float = 0.7) -> str:
        """非流式对话"""
        ...

    async def chat_stream(self, messages: list, temperature: float = 0.7):
        """流式对话"""
        ...
```

---

## 7. AI Prompt 设计

### 7.1 需求探索 Prompt

```
你是一个专业的需求分析师。根据用户的需求描述和选定的文档模板，通过结构化提问来深入了解需求细节。

当前探索维度：{dimension_label}
提问内容：{dimension_question}

用户原始需求：{raw_content}
已收集的信息：{explore_data}

请基于以上信息，用友好专业的语气向用户提问，帮助完善该维度的信息。如果用户之前已经提供了相关信息，请确认并补充细节。
```

### 7.2 标准化生成 Prompt

```
你是一个专业的需求文档撰写专家。请根据以下信息，按照{template_name}模板结构，生成一份完整的标准化需求文档。

用户原始需求：{raw_content}
探索收集的信息：{explore_data}
模板章节结构：{template_sections}

要求：
1. 严格按照模板章节结构组织文档
2. 将探索收集的信息填充到对应章节
3. 对于信息不完整的章节，用占位提示标注
4. 使用Markdown格式输出
5. 内容专业、完整、可追溯
```

### 7.3 文档调整 Prompt

```
你是一个需求文档审核专家。用户希望调整标准化文档的以下内容：

用户调整请求：{user_message}
当前文档内容：{current_content}

请分析用户的调整请求，给出具体的修改建议。建议应包含：
1. 修改的具体内容（可直接插入文档的文本）
2. 修改的位置（哪个章节）
3. 修改的理由
```

### 7.4 需求拆分 Prompt

```
你是一个需求分析专家。请将以下标准化需求文档拆分为独立的、可执行的单个需求项。

标准化文档内容：{standardized_content}

拆分规则：
1. 每个拆分项应是一个独立的功能需求或非功能需求
2. 拆分项应具有可测试性
3. 拆分粒度适中，不宜过大或过小
4. 保持需求项之间的逻辑关系
5. 按功能模块分组

请以JSON数组格式输出，每个元素包含content字段。
```

---

## 8. 错误码设计

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权或Token无效 |
| 404 | 资源不存在 |
| 2001 | 需求不存在 |
| 2002 | 需求状态不允许此操作 |
| 2003 | 文件格式不支持 |
| 2004 | 文件大小超限 |
| 2005 | 模板不存在 |
| 2006 | 探索会话不存在 |
| 2007 | 版本不存在 |
| 2008 | 拆分项不存在 |
| 2009 | AI服务调用失败 |
| 2010 | 文件解析失败 |

---

## 9. 开发任务清单

### 任务1：基础设施
- [ ] 创建统一响应格式封装（response.py）
- [ ] 更新config.py，新增上传目录和AI相关配置
- [ ] 创建requirement.py模型文件，定义所有新增ORM模型
- [ ] 扩展db_models.py中的Requirement和SplitRequirement模型

### 任务2：数据模型层
- [ ] 创建schemas/requirement.py，定义需求管理请求/响应模型
- [ ] 创建schemas/template.py，定义模板相关模型
- [ ] 创建schemas/explore.py，定义AI探索相关模型
- [ ] 创建schemas/standardize.py，定义标准化相关模型
- [ ] 创建schemas/version.py，定义版本管理模型
- [ ] 创建schemas/split.py，定义需求拆分模型

### 任务3：服务层
- [ ] 创建services/file_service.py，实现文件上传和解析
- [ ] 创建services/template_service.py，实现模板管理
- [ ] 创建services/requirement_service.py，实现需求CRUD
- [ ] 创建services/explore_service.py，实现AI需求探索
- [ ] 创建services/standardize_service.py，实现文档标准化和调整
- [ ] 创建services/version_service.py，实现版本管理
- [ ] 创建services/split_service.py，实现需求拆分
- [ ] 创建services/export_service.py，实现文档导出

### 任务4：AI层
- [ ] 创建ai/llm_client.py，封装大模型调用
- [ ] 创建ai/prompts/explore.py，需求探索Prompt模板
- [ ] 创建ai/prompts/standardize.py，标准化生成Prompt模板
- [ ] 创建ai/prompts/adjust.py，文档调整Prompt模板
- [ ] 创建ai/prompts/split.py，需求拆分Prompt模板

### 任务5：路由层
- [ ] 创建routers/requirement.py，需求管理路由
- [ ] 创建routers/template.py，模板管理路由
- [ ] 创建routers/explore.py，AI需求探索路由
- [ ] 创建routers/standardize.py，文档标准化路由
- [ ] 创建routers/version.py，版本管理路由
- [ ] 创建routers/split.py，需求拆分路由

### 任务6：应用集成
- [ ] 更新main.py，注册所有新路由
- [ ] 更新requirements.txt，新增依赖
- [ ] 验证所有接口正常工作

---

**文档版本**：v1.0
**创建日期**：2026-05-25
**维护者**：后端开发团队
