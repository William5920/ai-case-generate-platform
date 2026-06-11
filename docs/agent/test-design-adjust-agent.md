# TestDesignAdjustAgent - 测试设计 AI 调整 Agent

## 概述

TestDesignAdjustAgent 是测试设计阶段的 AI 调整智能体，支持用户通过对话方式对已生成的测试点和测试用例进行调整。AI 可以根据用户的需求补充新的测试点/用例，或删除已有的测试点/用例，同时尊重用户标记保留的节点。

**源码位置**: `backend/app/services/test_design.py`（`TestDesignService` 中 AI 调整相关方法）

## 架构设计

### 核心数据模型

- **AISession**: AI 调整会话，记录需求 ID、节点 ID、节点类型、标记保留的节点
- **AIMessage**: AI 调整对话消息，记录角色、内容、消息类型等

### 支持的节点类型

| 节点类型 | 说明 | 可调整内容 |
|---------|------|-----------|
| `requirement` | 拆分需求节点 | 测试点的增删 |
| `testPoint` | 测试点节点 | 测试用例的增删 |

## 核心方法

### 1. start_ai_session（启动 AI 调整会话）

```python
async def start_ai_session(self, db, data: AIAdjustStart) -> Dict[str, Any]
```

**功能**: 创建 AI 调整会话，构建初始系统提示词

**执行逻辑**:
1. 创建 `AISession` 记录
2. 获取节点上下文（已有测试点/用例列表）
3. 构建系统提示词（含节点内容、已有项、标记保留项）
4. 保存系统消息到数据库

**系统提示词特点**:
- 包含当前节点的完整上下文
- 明确标记保留的节点不可删除或修改
- 除非用户明确要求删除，否则只新增不删除
- 要求 AI 在给出建议时使用 `pending_nodes` 格式

### 2. send_ai_message（发送 AI 调整消息）

```python
async def send_ai_message(self, db, session_id, content) -> Dict[str, Any]
```

**功能**: 处理用户的调整请求，生成 AI 回复

**执行逻辑**:
1. 保存用户消息
2. 加载完整对话历史
3. 使用 `TEST_DESIGN_ADJUST_SCHEMA` 调用 LLM
4. 解析 AI 返回的调整建议
5. 如果是 proposal 类型，构建待确认的脑图数据

**返回值**:
- `type`: 消息类型（`proposal`/`discussion`）
- `content`: AI 回复文本
- `pendingMindmapData`: 待确认的脑图数据（proposal 时）

## 提示词模板

### TEST_DESIGN_ADJUST_SCHEMA

AI 调整的输出格式定义：

```json
{
  "content": "回复文本",
  "type": "proposal|discussion",
  "change_summary": "变更摘要",
  "pending_nodes": [
    {
      "action": "add|remove",
      "text": "节点文本（新增时必填）",
      "id": "节点ID（删除时必填）",
      "description": "描述（仅测试点新增时可选）",
      "case_property": "正例/反例（仅测试用例新增时必填）",
      "pre_condition": "前置条件（仅测试用例新增时可选）",
      "steps": [...]
    }
  ]
}
```

### 系统提示词（需求节点）

```
你是一个专业的测试设计专家。以下是当前需求的拆分内容和已有的测试点，
请基于这些信息帮助用户调整、补充或重新生成测试点。

【当前需求拆分内容】
{node_text}

【已有测试点】
{existing_items}

【标记保留的测试点ID】
{marked_node_ids}

注意：标记保留的测试点不可删除或修改其内容。
```

### 系统提示词（测试点节点）

```
你是一个专业的测试设计专家。以下是当前测试点的内容和已有的测试用例，
请基于这些信息帮助用户调整、补充或重新生成测试用例（包含正例和反例）。

【当前测试点内容】
{node_text}

【已有测试用例】
{existing_items}

【标记保留的测试用例ID】
{marked_node_ids}

注意：标记保留的测试用例不可删除或修改其内容。
```

## 标记保留机制

- 用户可以在脑图中标记某些节点为"保留"
- 标记保留的节点在 AI 调整时不可被删除或修改
- AI 只能在保留节点的基础上新增或调整其他节点
- 除非用户明确要求删除，AI 默认只新增不删除

## 降级策略

- LLM 不可用时，返回"AI服务暂时不可用"提示

## 与其他模块的关系

- **TestDesignService**: 作为测试设计服务的一部分，管理脑图数据的增删改
- **TestPointAgent / TestCaseAgent**: AI 调整是对自动生成结果的补充和修正
