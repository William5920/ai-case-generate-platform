# TestDesignOrchestrator - 测试设计编排器

## 概述

TestDesignOrchestrator 是测试设计的核心编排器，负责协调 TestPointAgent 和 TestCaseAgent 的执行流程。它从数据库中读取拆分后的需求，依次调用测试点生成和测试用例生成，并将结果持久化到数据库中。

**源码位置**: `backend/app/agents/orchestrator.py`

## 架构设计

### 类定义

```python
class TestDesignOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.kb_service = KnowledgeBaseService()
        self.rag_service = RAGService(self.kb_service, self.llm_client)
```

### 依赖组件

| 组件 | 说明 |
|------|------|
| `LLMClient` | 大语言模型调用客户端 |
| `KnowledgeBaseService` | 知识库管理服务 |
| `RAGService` | 知识库检索与重排服务 |

## 执行流程

```
读取拆分需求列表
    │
    ▼
遍历每个 SplitRequirement
    │
    ├──▶ 调用 TestPointAgent 生成测试点
    │        │
    │        ▼
    │    保存 TestPoint 到数据库
    │        │
    │        ▼
    │    遍历每个 TestPoint
    │        │
    │        └──▶ 调用 TestCaseAgent 生成测试用例
    │                 │
    │                 ▼
    │             保存 TestCase 到数据库
    │
    ▼
更新 Requirement 状态为 completed
```

## 核心方法

### run()

```python
async def run(
    self,
    db: AsyncSession,
    requirement_id: str,
    use_knowledge_base: bool,
    progress_callback: Optional[ProgressCallback] = None,
) -> None
```

**参数说明**:
- `db`: 异步数据库会话
- `requirement_id`: 需求 ID
- `use_knowledge_base`: 是否启用知识库增强
- `progress_callback`: 进度回调函数，签名为 `async (progress: int, message: str) -> None`

**执行逻辑**:

1. **读取拆分需求**: 从数据库查询 `SplitRequirement` 列表
2. **空需求处理**: 如果没有拆分需求，直接标记为 completed
3. **遍历生成**:
   - 对每个拆分需求调用 `run_test_point_agent()` 生成测试点
   - 测试点生成失败时使用默认测试点（功能验证、边界条件验证、异常处理验证）
   - 对每个测试点调用 `run_test_case_agent()` 生成测试用例
   - 用例生成失败时使用默认用例（1个正例 + 1个反例）
4. **进度上报**: 通过 `progress_callback` 上报进度
5. **状态更新**: 完成后将需求状态更新为 `completed`

### close()

```python
async def close(self) -> None
```

关闭 LLM 客户端连接，释放资源。

## 降级策略

### 测试点生成降级

当 TestPointAgent 返回空结果时，使用以下默认测试点：

```python
[
    {"text": "功能验证", "category": "功能验证", "rationale": "默认测试点"},
    {"text": "边界条件验证", "category": "边界条件", "rationale": "默认测试点"},
    {"text": "异常处理验证", "category": "异常处理", "rationale": "默认测试点"},
]
```

### 测试用例生成降级

当 TestCaseAgent 返回空结果时，使用以下默认用例：

```python
[
    {"name": "{测试点}-正例", "property": "正例", ...},
    {"name": "{测试点}-反例", "property": "反例", ...},
]
```

## 数据模型关系

```
Requirement (需求)
  └── SplitRequirement (拆分需求)
        └── TestPoint (测试点)
              └── TestCase (测试用例)
```

## 与其他 Agent 的关系

- **调用 TestPointAgent**: 为每个拆分需求生成测试点
- **调用 TestCaseAgent**: 为每个测试点生成测试用例
- **使用 RAGService**: 通过知识库增强测试点和用例的生成质量
