# TestPointAgent - 测试点生成 Agent

## 概述

TestPointAgent 是基于 LangGraph 构建的测试点生成智能体，负责从需求文本中自动提取并生成高质量的测试点。该 Agent 采用多步骤工作流，包含需求分析、知识召回、测试点生成、自评审和优化精炼等环节，通过自我迭代确保测试点质量。

**源码位置**: `backend/app/agents/test_point_agent.py`

## 架构设计

### 状态定义 (TestPointState)

| 字段 | 类型 | 说明 |
|------|------|------|
| `requirement_text` | `str` | 原始需求文本 |
| `use_knowledge_base` | `bool` | 是否使用知识库 |
| `requirement_analysis` | `Optional[str]` | 需求分析结果（JSON） |
| `knowledge_context` | `Optional[str]` | 知识库召回的上下文 |
| `test_points` | `Optional[List[Dict]]` | 生成的测试点列表 |
| `review_result` | `Optional[Dict]` | 自评审结果 |
| `retry_count` | `int` | 当前重试次数 |
| `max_retries` | `int` | 最大重试次数（默认2） |
| `final_test_points` | `Optional[List[Dict]]` | 最终输出的测试点 |

### 工作流图

```
START → analyze_requirement → recall_knowledge → generate_test_points → self_review
                                                                            │
                                                                    ┌───────┴───────┐
                                                                    │               │
                                                              refine_points     output → END
                                                                    │
                                                                    └──→ self_review (循环)
```

## 节点详解

### 1. analyze_requirement（需求分析）

- **功能**: 分析原始需求文本，提取关键信息
- **LLM 模型**: `settings.OPENAI_MODEL_ANALYZE`
- **温度**: 0.3（偏确定性输出）
- **分析维度**:
  - 核心功能点
  - 输入输出
  - 约束条件
  - 边界条件
  - 关联依赖
  - 异常场景
- **输出格式**: JSON 结构，包含 `core_functions`、`inputs_outputs`、`constraints`、`boundary_conditions`、`dependencies`、`exception_scenarios`

### 2. recall_knowledge（知识召回）

- **功能**: 根据需求分析结果，从知识库中检索相关知识
- **条件执行**: 当 `use_knowledge_base=True` 时才执行，否则返回空字符串
- **检索策略**:
  1. 使用需求分析中的核心功能点作为查询
  2. 调用 `RAGService.recall_and_rerank()` 进行检索+重排
  3. 参数: `top_k=5`, `threshold=0.7`, `final_k=3`
- **输出**: 格式化的参考文档列表，包含相关度分数

### 3. generate_test_points（生成测试点）

- **功能**: 根据需求分析和知识库上下文生成测试点
- **LLM 模型**: `settings.OPENAI_MODEL_GENERATE`
- **温度**: 0.7（偏创造性输出）
- **生成要求**:
  - 每个测试点覆盖一个独立的测试维度
  - 包含功能验证、边界条件、异常处理、兼容性等维度
  - 测试点名称格式为"动词+对象+条件/场景"
  - 生成 3-7 个测试点
  - 结合参考知识中的测试规范和领域经验
- **输出格式**: 每个测试点包含 `text`（名称）、`category`（类别）、`rationale`（理由）

### 4. self_review（自评审）

- **功能**: 对生成的测试点进行质量评审
- **LLM 模型**: `settings.OPENAI_MODEL_ANALYZE`
- **温度**: 0.3
- **评审维度**（每项 1-5 分）:
  - 完整性：是否覆盖了需求的所有关键功能点
  - 独立性：测试点之间是否相互独立，无重复
  - 可测性：每个测试点是否可以明确地设计测试用例
  - 规范性：测试点命名是否规范，含义是否清晰
  - 领域性：是否结合了领域知识
- **通过条件**: 平均分 >= 3.5 且不存在严重问题（如"缺少"关键词的问题）

### 5. refine_points（优化精炼）

- **功能**: 根据评审反馈优化测试点
- **触发条件**: 自评审未通过且重试次数未达上限
- **LLM 模型**: `settings.OPENAI_MODEL_GENERATE`
- **温度**: 0.7
- **优化要求**:
  - 针对评审指出的问题逐一修正
  - 补充遗漏的测试维度
  - 合并或拆分重复/模糊的测试点
  - 保持测试点总数在 3-7 个

### 6. output（输出）

- **功能**: 将最终测试点写入 `final_test_points` 字段

## 条件路由

### should_refine

- 评审通过（`passed=True`）或重试次数 >= `max_retries` → 输出结果
- 否则 → 进入优化精炼环节

## 入口函数

```python
async def run_test_point_agent(
    requirement_text: str,
    use_knowledge_base: bool,
    llm_client: LLMClient,
    rag_service: RAGService,
    max_retries: int = 2,
) -> List[Dict]
```

**参数说明**:
- `requirement_text`: 需求文本
- `use_knowledge_base`: 是否启用知识库增强
- `llm_client`: LLM 客户端实例
- `rag_service`: RAG 检索服务实例
- `max_retries`: 最大自纠正次数

**返回值**: 测试点列表，每个测试点包含 `text`、`category`、`rationale` 字段

## 依赖关系

- `LLMClient`: 大语言模型调用客户端
- `RAGService`: 知识库检索与重排服务
- `PromptTemplates`: 提示词模板集合
