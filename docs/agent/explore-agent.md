# ExploreAgent - 需求探索 Agent

## 概述

ExploreAgent 是需求探索阶段的智能体，通过多轮对话引导用户逐步补充需求的各个维度信息。它基于文档模板的维度定义，按顺序引导用户回答问题，收集完整的需求信息，为后续的标准化文档生成提供数据支撑。

**源码位置**: `backend/app/services/explore_service.py`（`ExploreService` 类）

## 架构设计

### 类定义

```python
class ExploreService:
    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)
```

### 核心数据模型

- **ExploreMessage**: 探索对话消息，包含角色、内容、维度信息、快捷回复等
- **Requirement**: 需求实体，存储探索数据（`explore_data` 字段）

## 工作流程

```
start_explore (开始探索)
    │
    ▼
获取模板维度列表 → 生成第一个维度的问题
    │
    ▼
send_explore_message (用户回复)
    │
    ├── 记录用户消息到数据库
    ├── 更新 explore_data
    ├── 计算理解度分数
    ├── 判断是否可以生成文档
    │
    ├── 还有未探索维度 → 生成下一个维度的问题
    │
    └── 所有维度已探索 → 生成总结消息
```

## 核心方法

### 1. start_explore（开始探索）

```python
async def start_explore(
    self, db, user_id, requirement_id, template_id,
    raw_content=None, file_id=None
) -> dict
```

**功能**: 启动需求探索会话

**执行逻辑**:
1. 查询需求记录，解析文件内容（如有）
2. 获取模板维度列表
3. 更新需求状态为 `exploring`
4. 使用 `EXPLORE_START` 提示词生成第一个维度的问题
5. 保存 AI 消息到数据库

**返回值**:
- `sessionId`: 探索会话 ID
- `totalDimensions`: 总维度数
- `firstQuestion`: 第一个维度的问题信息

### 2. send_explore_message（发送探索消息）

```python
async def send_explore_message(
    self, db, user_id, requirement_id, message,
    dimension_key=None, session_id=None
) -> dict
```

**功能**: 处理用户回复并生成下一个问题

**执行逻辑**:
1. 保存用户消息到数据库
2. 更新已回复状态
3. 更新 `explore_data`（追加当前维度的用户回复）
4. 计算理解度分数
5. 确定下一个待探索维度
6. 使用 `EXPLORE_CHAT` 提示词生成 AI 回复
7. 保存 AI 消息到数据库

**返回值**:
- `exploredDimensions`: 已探索的维度列表
- `understandingScore`: 理解度分数
- `canGenerate`: 是否可以生成文档
- `dimensionKey`/`dimensionLabel`: 下一个维度信息

### 3. get_explore_history（获取探索历史）

获取指定需求的全部探索对话记录。

### 4. get_explore_status（获取探索状态）

获取探索会话的当前状态，包括进度、理解度等。

## 提示词模板

### EXPLORE_START

用于生成第一个维度的问题，AI 会：
1. 简要复述用户需求的核心要点
2. 针对第一个维度提出问题
3. 问题具体、有针对性

### EXPLORE_CHAT

用于处理用户回复并继续探索，AI 会：
1. 确认并总结用户在该维度提供的信息
2. 如果信息不够充分，追问细节
3. 如果信息已充分，提出下一个维度的提问

**输出格式** (JSON):
```json
{
  "summary": "对用户回复的简要总结",
  "type": "question|followup|summary",
  "content": "回复内容",
  "dimension_key": "下一个维度标识",
  "dimension_label": "下一个维度名称",
  "quick_replies": ["快捷回复1", "快捷回复2"]
}
```

## 理解度计算

```python
def _calculate_understanding_score(self, explored_keys, total, latest_message=""):
    base_score = int((len(explored_keys) / total) * 80)
    richness_bonus = min(20, len(latest_message) // 10) if len(latest_message) > 50 else 0
    return min(100, base_score + richness_bonus)
```

- **基础分**: 已探索维度数 / 总维度数 * 80
- **丰富度加分**: 最新消息长度 > 50 时，每 10 个字符加 1 分，上限 20 分
- **总分上限**: 100

**可生成条件**: 理解度 >= 80 或已探索所有维度

## 降级策略

- LLM 不可用时，使用模板维度的问题文本作为默认回复
- 文件解析失败时，跳过文件内容解析，使用已有的 `raw_content`

## 与其他模块的关系

- **TemplateService**: 获取模板维度定义和问题
- **StandardizeService**: 探索完成后，使用 `explore_data` 生成标准化文档
- **FileService**: 解析上传文件的内容
