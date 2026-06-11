# TestCaseAgent - 测试用例生成 Agent

## 概述

TestCaseAgent 是基于 LangGraph 构建的测试用例生成智能体，负责根据测试点和需求上下文自动生成高质量、可执行的测试用例。该 Agent 采用多步骤工作流，包含测试点分析、知识召回、用例生成、质量校验和自我纠正等环节，通过自我迭代确保测试用例质量。

**源码位置**: `backend/app/agents/test_case_agent.py`

## 架构设计

### 状态定义 (TestCaseState)

| 字段 | 类型 | 说明 |
|------|------|------|
| `test_point_text` | `str` | 测试点文本 |
| `test_point_category` | `str` | 测试点类别 |
| `requirement_context` | `str` | 需求上下文 |
| `use_knowledge_base` | `bool` | 是否使用知识库 |
| `knowledge_context` | `Optional[str]` | 知识库召回的上下文 |
| `test_point_analysis` | `Optional[str]` | 测试点分析结果（JSON） |
| `test_cases` | `Optional[List[Dict]]` | 生成的测试用例列表 |
| `quality_result` | `Optional[Dict]` | 质量校验结果 |
| `retry_count` | `int` | 当前重试次数 |
| `max_retries` | `int` | 最大重试次数（默认2） |
| `final_test_cases` | `Optional[List[Dict]]` | 最终输出的测试用例 |

### 工作流图

```
START → analyze_test_point → recall_knowledge → generate_test_cases → quality_check
                                                                            │
                                                                    ┌───────┴───────┐
                                                                    │               │
                                                              self_correct     output → END
                                                                    │
                                                                    └──→ quality_check (循环)
```

## 节点详解

### 1. analyze_test_point（测试点分析）

- **功能**: 分析测试点，确定用例设计方向
- **LLM 模型**: `settings.OPENAI_MODEL_ANALYZE`
- **温度**: 0.3
- **分析内容**:
  - 测试意图：这个测试点要验证什么
  - 需要的用例类型：需要哪些正例和反例
  - 关键输入：测试需要哪些输入数据
  - 预期行为：正常和异常情况下系统应如何响应
- **输出格式**: JSON 结构，包含 `test_intent`、`case_types_needed`、`key_inputs`、`expected_behaviors`

### 2. recall_knowledge（知识召回）

- **功能**: 根据测试点信息，从知识库中检索相关知识
- **条件执行**: 当 `use_knowledge_base=True` 时才执行
- **检索策略**:
  1. 使用测试点文本和类别构建查询
  2. 调用 `RAGService.recall_and_rerank()` 进行检索+重排
  3. 参数: `top_k=5`, `threshold=0.7`, `final_k=3`
- **输出**: 格式化的参考文档列表，包含相关度分数

### 3. generate_test_cases（生成测试用例）

- **功能**: 根据测试点分析和知识库上下文生成测试用例
- **LLM 模型**: `settings.OPENAI_MODEL_GENERATE`
- **温度**: 0.7
- **生成要求**:
  - 至少生成 2 个用例：1 个正例 + 1 个反例
  - 正例覆盖正常流程和主要边界值
  - 反例覆盖无效输入和异常场景
  - 每个用例包含完整的前置条件、步骤和预期结果
  - 步骤应具体可执行，预期结果应可验证
  - 结合参考知识中的用例编写规范和示例
- **输出格式**: 每个用例包含 `name`、`property`（正例/反例）、`pre_condition`、`steps`（含 `name`、`description`、`stepExpectedResult`）

### 4. quality_check（质量校验）

- **功能**: 对生成的测试用例进行质量校验
- **LLM 模型**: `settings.OPENAI_MODEL_ANALYZE`
- **温度**: 0.3
- **校验维度**（每项 1-5 分）:
  - 完整性：每个用例是否有前置条件、步骤、预期结果
  - 可执行性：步骤描述是否具体、可操作
  - 可验证性：预期结果是否明确、可判定通过/失败
  - 正反例均衡：是否包含正例和反例，比例是否合理
  - 规范性：用例命名是否规范，步骤是否有逻辑顺序
- **通过条件**: 平均分 >= 3.5 且不存在严重问题（如"缺少"或"无"关键词的问题）

### 5. self_correct（自我纠正）

- **功能**: 根据质量校验反馈修正测试用例
- **触发条件**: 质量校验未通过且重试次数未达上限
- **LLM 模型**: `settings.OPENAI_MODEL_GENERATE`
- **温度**: 0.7
- **修正要求**:
  - 针对校验指出的问题逐一修正
  - 补充遗漏的用例类型（如缺少反例则补充反例）
  - 完善前置条件和步骤描述
  - 确保预期结果明确可验证

### 6. output（输出）

- **功能**: 将最终测试用例写入 `final_test_cases` 字段

## 条件路由

### should_correct

- 质量校验通过（`passed=True`）或重试次数 >= `max_retries` → 输出结果
- 否则 → 进入自我纠正环节

## 入口函数

```python
async def run_test_case_agent(
    test_point_text: str,
    test_point_category: str,
    requirement_context: str,
    use_knowledge_base: bool,
    llm_client: LLMClient,
    rag_service: RAGService,
    max_retries: int = 2,
) -> List[Dict]
```

**参数说明**:
- `test_point_text`: 测试点文本
- `test_point_category`: 测试点类别（功能验证/边界条件/异常处理/兼容性/性能/安全）
- `requirement_context`: 需求上下文
- `use_knowledge_base`: 是否启用知识库增强
- `llm_client`: LLM 客户端实例
- `rag_service`: RAG 检索服务实例
- `max_retries`: 最大自纠正次数

**返回值**: 测试用例列表，每个用例包含 `name`、`property`、`pre_condition`、`steps` 字段

## 依赖关系

- `LLMClient`: 大语言模型调用客户端
- `RAGService`: 知识库检索与重排服务
- `PromptTemplates`: 提示词模板集合
