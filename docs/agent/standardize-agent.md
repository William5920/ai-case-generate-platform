# StandardizeAgent - 需求标准化 Agent

## 概述

StandardizeAgent 是需求标准化阶段的智能体，负责将用户的原始需求文本和探索收集的信息，按照选定的文档模板结构，生成一份完整的标准化需求文档。同时支持通过对话方式对文档进行调整和修改。

**源码位置**: `backend/app/services/standardize_service.py`（`StandardizeService` 类）

## 架构设计

### 类定义

```python
class StandardizeService:
    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)
```

### 核心数据模型

- **Requirement**: 需求实体，存储标准化内容（`standardized_content` 字段）
- **AdjustMessage**: 调整对话消息，包含角色、内容、建议内容、变更摘要等
- **DocVersion**: 文档版本记录

## 核心方法

### 1. process_standardize（生成标准化文档）

```python
async def process_standardize(
    self, db, user_id, requirement_id, template_id, input_mode,
    raw_content=None, file_id=None, explore_data=None
) -> dict
```

**功能**: 根据原始需求和探索数据生成标准化文档

**执行逻辑**:
1. 查询需求记录
2. 解析文件内容（如有 file_id）
3. 获取模板详情和章节结构
4. 使用 `STANDARDIZE_GENERATE` 提示词调用 LLM 生成文档
5. 保存标准化内容和文档版本
6. 更新需求状态为 `standardized`

**返回值**:
- `standardizedContent`: 标准化文档内容（Markdown 格式）
- `versionId`: 版本 ID
- `versionNumber`: 版本号

### 2. send_adjust_message（发送调整消息）

```python
async def send_adjust_message(
    self, db, user_id, requirement_id, message,
    current_content, template_id=None, context=None
) -> dict
```

**功能**: 处理用户对文档的调整请求

**执行逻辑**:
1. 保存用户消息到数据库
2. 使用 `STANDARDIZE_ADJUST` 提示词调用 LLM
3. 解析 AI 返回的调整建议
4. 保存 AI 消息到数据库

**返回值**:
- `type`: 消息类型（`proposal`/`discussion`/`clarification`）
- `proposal`: 建议内容（当 type 为 proposal 时）
  - `pendingContent`: 修改后的完整文档内容
  - `changeSummary`: 变更摘要

### 3. adopt_proposal（采纳建议）

```python
async def adopt_proposal(self, db, user_id, message_id, requirement_id) -> dict
```

**功能**: 采纳 AI 的调整建议，更新文档内容并创建新版本

### 4. reject_proposal（拒绝建议）

```python
async def reject_proposal(self, db, user_id, message_id, requirement_id) -> None
```

**功能**: 拒绝 AI 的调整建议

### 5. get_adjust_history（获取调整历史）

获取指定需求的全部调整对话记录。

### 6. get_standardized_result（获取标准化结果）

获取最新的标准化文档内容和版本信息。

## 提示词模板

### STANDARDIZE_GENERATE

用于生成标准化文档，要求：
- 严格按照模板章节结构组织文档（Markdown 格式）
- 将探索收集的信息填充到对应章节
- 信息不完整的章节用 `> 待补充：...` 标注
- 功能需求章节应详细描述输入、输出、业务规则
- 非功能需求章节应包含量化指标

### STANDARDIZE_ADJUST

用于处理文档调整请求，AI 会：
1. 理解用户的调整意图
2. 给出修改后的完整文档内容
3. 总结变更内容

**输出格式** (JSON):
```json
{
  "content": "回复文本（说明修改了什么）",
  "type": "proposal|discussion|clarification",
  "pending_content": "修改后的完整文档内容（Markdown格式）",
  "change_summary": "变更摘要描述"
}
```

## 版本管理

- 每次生成标准化文档时创建初始版本（version_number = 1）
- 每次采纳建议时创建新版本，版本号递增
- 版本记录包含内容、描述和创建时间

## 降级策略

- LLM 不可用时，使用 `_generate_fallback_content()` 生成基础模板文档
- 降级文档包含原始需求文本和模板章节占位符
- 底部标注"AI服务暂不可用，请手动补充"

## 与其他模块的关系

- **ExploreService**: 接收探索阶段收集的 `explore_data`
- **TemplateService**: 获取模板名称、章节结构
- **FileService**: 解析上传文件的内容
- **SplitService**: 标准化完成后，对文档进行需求拆分
