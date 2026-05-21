# 智能测试用例生成 Agent 设计文档

## 1. 背景与问题分析

### 1.1 现状

当前测试点生成和测试用例生成采用简单的 LLM 单轮对话方式：

- **测试点生成**（`_generate_test_points_for_split_req`）：发送简单 prompt，解析行文本，无结构化输出
- **测试用例生成**（`_generate_test_cases_for_point`）：发送 prompt 请求 JSON 格式，正则提取，无质量校验
- **知识库**：Milvus 向量库 + 文档切片 + 召回测试已实现，但**完全未集成**到生成流程
- **`use_knowledge_base` 参数**：Task 模型中存在但从未使用
- **失败回退**：硬编码通用测试点/用例（"功能验证"、"边界条件验证"等）

### 1.2 核心问题

| 问题 | 影响 |
|------|------|
| 无知识库集成 | 生成的测试点/用例缺乏领域知识，通用性强但专业性不足 |
| 无结构化推理 | LLM 单轮生成，无法进行需求分析→知识检索→生成→校验的多步推理 |
| 无质量校验 | 生成的用例可能缺少前置条件、步骤不完整、正反例不均衡 |
| 无自我修正 | 一次生成定终身，无法根据质量反馈迭代优化 |
| Prompt 过于简单 | 缺乏角色设定、输出约束、示例引导，LLM 输出质量不稳定 |
| 解析脆弱 | 正则提取 JSON 容易失败，回退到硬编码内容 |

### 1.3 设计目标

1. **知识库 RAG 集成**：生成时自动检索知识库中的相关内容，注入领域知识
2. **多步推理**：通过 LangGraph StateGraph 实现分析→召回→生成→校验→修正的完整流程
3. **质量闭环**：生成后自动校验，不达标时自我修正（最多 2 轮）
4. **结构化输出**：使用 JSON Schema 约束 LLM 输出格式，减少解析失败
5. **可观测性**：每个步骤的中间结果可追踪、可调试

---

## 2. 整体架构

### 2.1 架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                    TestDesignOrchestrator                     │
│                   (编排层，替代原 _run_generation)             │
├────────────────────────┬────────────────────────────────────┤
│                        │                                    │
│  ┌─────────────────────▼──────────────────────┐             │
│  │         TestPointAgent (LangGraph)          │             │
│  │                                             │             │
│  │  analyze_requirement → recall_knowledge     │             │
│  │       → generate → self_review              │             │
│  │       → [refine] → output                   │             │
│  └─────────────────────┬──────────────────────┘             │
│                        │ 测试点列表                           │
│  ┌─────────────────────▼──────────────────────┐             │
│  │         TestCaseAgent (LangGraph)           │             │
│  │                                             │             │
│  │  analyze_test_point → recall_knowledge      │             │
│  │       → generate → quality_check            │             │
│  │       → [self_correct] → output             │             │
│  └─────────────────────────────────────────────┘             │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                    共享基础设施层                              │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐   │
│  │ LLM Client │  │ RAG Service│  │ KnowledgeBaseService │   │
│  │ (OpenAI)   │  │ (召回+重排) │  │ (Milvus)            │   │
│  └────────────┘  └────────────┘  └─────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 调用关系

```
TestDesignService._run_generation()
    │
    ├── TestDesignOrchestrator.run(requirement_id, use_knowledge_base)
    │       │
    │       ├── 对每个 SplitRequirement:
    │       │       │
    │       │       ├── TestPointAgent.invoke(state)
    │       │       │     → 输出: List[TestPointItem]
    │       │       │
    │       │       └── 对每个 TestPointItem:
    │       │               │
    │       │               └── TestCaseAgent.invoke(state)
    │       │                     → 输出: List[TestCaseItem]
    │       │
    │       └── 持久化到数据库
    │
    └── 更新任务进度
```

---

## 3. 共享基础设施

### 3.1 LLM Client 封装

封装 OpenAI API 调用，统一管理模型参数、重试、错误处理：

```python
class LLMClient:
    async def chat(
        self,
        messages: List[Dict],
        model: str = None,
        temperature: float = 0.7,
        response_format: Optional[Dict] = None,  # JSON Mode
        max_tokens: int = 4096,
    ) -> str:
        """非流式调用，返回 assistant 消息内容"""

    async def chat_with_schema(
        self,
        messages: List[Dict],
        schema: Dict,  # JSON Schema
        model: str = None,
        temperature: float = 0.5,
    ) -> Dict:
        """结构化输出，使用 JSON Mode + Schema 约束"""
```

**关键设计决策**：
- 使用 OpenAI 的 `response_format: {"type": "json_object"}` 强制 JSON 输出
- 在 system prompt 中嵌入 JSON Schema 描述，确保输出格式稳定
- 优先使用 `gpt-4o-mini` 进行分析和校验步骤，`gpt-4o` 用于核心生成步骤（成本优化）
- 内置指数退避重试（3 次），处理 rate limit

### 3.2 RAG Service

封装知识库检索逻辑，提供面向 Agent 的简洁接口：

```python
class RAGService:
    async def recall(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
        strategy: str = "hybrid",
    ) -> List[RecallResult]:
        """检索知识库，返回相关文档切片"""

    async def recall_and_rerank(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
        final_k: int = 3,
    ) -> List[RecallResult]:
        """检索 + LLM 重排序，返回最相关的 final_k 条结果"""
```

**召回策略**：

| 策略 | 实现 | 适用场景 |
|------|------|----------|
| vector | Milvus 向量相似度搜索 | 语义相近但用词不同的内容 |
| hybrid | 向量搜索 + BM25 关键词匹配，加权融合 | 包含专业术语、编号规则的文档 |
| rerank | 向量搜索后，LLM 对 top_k 结果重排序 | 需要高精度召回的场景 |

**LLM 重排序 Prompt**：

```
你是一个知识检索专家。请根据查询问题，对以下检索结果按相关性从高到低重新排序。
只返回排序后的编号列表，用逗号分隔。

查询问题：{query}

检索结果：
1. {chunk_1}
2. {chunk_2}
...

排序结果：
```

### 3.3 Prompt 模板管理

所有 Prompt 模板集中管理，支持变量注入：

```python
class PromptTemplates:
    TEST_POINT_ANALYZE = """..."""
    TEST_POINT_GENERATE = """..."""
    TEST_POINT_REVIEW = """..."""
    TEST_POINT_REFINE = """..."""
    TEST_CASE_ANALYZE = """..."""
    TEST_CASE_GENERATE = """..."""
    TEST_CASE_QUALITY_CHECK = """..."""
    TEST_CASE_SELF_CORRECT = """..."""
    RAG_RERANK = """..."""
```

---

## 4. TestPointAgent 详细设计

### 4.1 状态定义

```python
class TestPointState(TypedDict):
    requirement_text: str                    # 输入：拆分需求文本
    use_knowledge_base: bool                 # 是否启用知识库
    requirement_analysis: Optional[str]      # 需求分析结果
    knowledge_context: Optional[str]         # 知识库召回内容
    test_points: Optional[List[Dict]]        # 生成的测试点
    review_result: Optional[Dict]            # 自我评审结果
    retry_count: int                         # 当前重试次数
    max_retries: int                         # 最大重试次数（默认2）
    final_test_points: Optional[List[Dict]]  # 最终输出
```

### 4.2 节点详细设计

#### 节点 1：analyze_requirement（需求分析）

**目的**：深入理解需求文本，提取关键功能点、约束条件、边界条件，为后续生成提供结构化输入。

**Prompt 设计**：

```
你是一个专业的测试分析专家。请分析以下需求，提取出关键信息。

需求文本：
{requirement_text}

请从以下维度分析：
1. 核心功能点：该需求要实现什么功能？
2. 输入输出：涉及哪些输入和预期输出？
3. 约束条件：有哪些业务规则、限制条件？
4. 边界条件：有哪些边界值、极端情况需要考虑？
5. 关联依赖：是否依赖其他功能或外部系统？
6. 异常场景：可能出现的异常或错误情况？

请以 JSON 格式输出分析结果。
```

**输出格式**：

```json
{
  "core_functions": ["功能1", "功能2"],
  "inputs_outputs": [{"input": "xxx", "output": "xxx"}],
  "constraints": ["约束1", "约束2"],
  "boundary_conditions": ["边界1", "边界2"],
  "dependencies": ["依赖1"],
  "exception_scenarios": ["异常1", "异常2"]
}
```

**模型选择**：`gpt-4o-mini`（分析任务不需要最强模型）

#### 节点 2：recall_knowledge（知识召回）

**目的**：从知识库中检索与当前需求相关的领域知识、测试规范、历史用例等。

**条件执行**：仅当 `use_knowledge_base == True` 时执行，否则跳过。

**执行逻辑**：

```python
async def recall_knowledge(state: TestPointState) -> dict:
    if not state["use_knowledge_base"]:
        return {"knowledge_context": ""}

    query = state["requirement_analysis"] or state["requirement_text"]
    results = await rag_service.recall_and_rerank(
        query=query,
        top_k=5,
        threshold=0.7,
        final_k=3,
    )

    if not results:
        return {"knowledge_context": ""}

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[参考文档{i}] (相关度: {r.score:.2f})\n{r.content}")

    return {"knowledge_context": "\n\n---\n\n".join(context_parts)}
```

#### 节点 3：generate_test_points（生成测试点）

**目的**：基于需求分析和知识库上下文，生成高质量的测试点。

**Prompt 设计**：

```
你是一个专业的测试设计专家。请根据以下需求分析和参考知识，生成测试点。

## 需求分析
{requirement_analysis}

## 参考知识
{knowledge_context}

## 原始需求
{requirement_text}

## 生成要求
1. 每个测试点应覆盖一个独立的测试维度
2. 测试点应包含：功能验证、边界条件、异常处理、兼容性等维度
3. 测试点名称应简洁明确，格式为"动词+对象+条件/场景"
4. 生成 3-7 个测试点
5. 如果有参考知识，请结合参考知识中的测试规范和领域经验

## 输出格式（JSON）
{{
  "test_points": [
    {{
      "text": "测试点名称",
      "category": "功能验证|边界条件|异常处理|兼容性|性能|安全",
      "rationale": "为什么需要这个测试点（简述）"
    }}
  ]
}}
```

**模型选择**：`gpt-4o`（核心生成步骤需要高质量输出）

**结构化输出**：使用 `response_format: {"type": "json_object"}` + system prompt 中的 JSON Schema 描述

#### 节点 4：self_review（自我评审）

**目的**：对生成的测试点进行质量评审，识别遗漏、重复或不合理的测试点。

**Prompt 设计**：

```
你是一个测试质量评审专家。请评审以下测试点列表的质量。

## 原始需求
{requirement_text}

## 需求分析
{requirement_analysis}

## 生成的测试点
{test_points_json}

## 评审维度（每项 1-5 分）
1. 完整性：是否覆盖了需求的所有关键功能点？
2. 独立性：测试点之间是否相互独立，无重复？
3. 可测性：每个测试点是否可以明确地设计测试用例？
4. 规范性：测试点命名是否规范，含义是否清晰？
5. 领域性：是否结合了领域知识（如有参考知识）？

## 输出格式（JSON）
{{
  "scores": {{
    "completeness": 4,
    "independence": 5,
    "testability": 4,
    "standardization": 3,
    "domain_relevance": 4
  }},
  "average_score": 4.0,
  "passed": true,
  "issues": [
    "缺少对并发场景的测试点",
    "测试点3和测试点5有部分重叠"
  ],
  "suggestions": [
    "增加并发场景的测试点",
    "合并测试点3和5"
  ]
}}
```

**通过标准**：`average_score >= 3.5` 且无严重问题（issues 中无 "缺少" 类问题）

**模型选择**：`gpt-4o-mini`

#### 节点 5：refine_points（优化测试点）

**目的**：根据评审反馈优化测试点，仅在评审未通过时执行。

**条件执行**：`review_result["passed"] == False` 且 `retry_count < max_retries`

**Prompt 设计**：

```
你是一个专业的测试设计专家。请根据评审反馈优化以下测试点。

## 原始需求
{requirement_text}

## 当前测试点
{test_points_json}

## 评审反馈
- 评分：{average_score}/5
- 问题：{issues}
- 建议：{suggestions}

## 优化要求
1. 针对评审指出的问题逐一修正
2. 补充遗漏的测试维度
3. 合并或拆分重复/模糊的测试点
4. 保持测试点总数在 3-7 个

## 输出格式（与生成步骤相同）
{{
  "test_points": [
    {{
      "text": "测试点名称",
      "category": "功能验证|边界条件|异常处理|兼容性|性能|安全",
      "rationale": "为什么需要这个测试点"
    }}
  ]
}}
```

**模型选择**：`gpt-4o`

### 4.3 图结构

```python
from langgraph.graph import StateGraph, END

def build_test_point_agent() -> CompiledGraph:
    graph = StateGraph(TestPointState)

    graph.add_node("analyze_requirement", analyze_requirement)
    graph.add_node("recall_knowledge", recall_knowledge)
    graph.add_node("generate_test_points", generate_test_points)
    graph.add_node("self_review", self_review)
    graph.add_node("refine_points", refine_points)
    graph.add_node("output", output_test_points)

    graph.set_entry_point("analyze_requirement")
    graph.add_edge("analyze_requirement", "recall_knowledge")
    graph.add_edge("recall_knowledge", "generate_test_points")
    graph.add_edge("generate_test_points", "self_review")

    graph.add_conditional_edges(
        "self_review",
        should_refine,
        {
            "refine": "refine_points",
            "output": "output",
        }
    )
    graph.add_edge("refine_points", "self_review")  # 回到评审
    graph.add_edge("output", END)

    return graph.compile()
```

**条件路由**：

```python
def should_refine(state: TestPointState) -> str:
    review = state.get("review_result", {})
    retry = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if review.get("passed", False) or retry >= max_retries:
        return "output"
    return "refine"
```

---

## 5. TestCaseAgent 详细设计

### 5.1 状态定义

```python
class TestCaseState(TypedDict):
    test_point_text: str                      # 输入：测试点文本
    test_point_category: str                  # 测试点类别
    requirement_context: str                  # 所属需求上下文
    use_knowledge_base: bool                  # 是否启用知识库
    knowledge_context: Optional[str]          # 知识库召回内容
    test_cases: Optional[List[Dict]]          # 生成的测试用例
    quality_result: Optional[Dict]            # 质量校验结果
    retry_count: int                          # 当前重试次数
    max_retries: int                          # 最大重试次数（默认2）
    final_test_cases: Optional[List[Dict]]    # 最终输出
```

### 5.2 节点详细设计

#### 节点 1：analyze_test_point（测试点分析）

**目的**：理解测试点的测试意图，确定需要生成的用例类型和覆盖范围。

**Prompt 设计**：

```
你是一个专业的测试用例设计专家。请分析以下测试点，确定用例设计方向。

## 需求上下文
{requirement_context}

## 测试点
- 名称：{test_point_text}
- 类别：{test_point_category}

请分析：
1. 测试意图：这个测试点要验证什么？
2. 需要的用例类型：需要哪些正例和反例？
3. 关键输入：测试需要哪些输入数据？
4. 预期行为：正常和异常情况下系统应如何响应？

## 输出格式（JSON）
{{
  "test_intent": "测试意图描述",
  "case_types_needed": ["正例-正常流程", "正例-边界值", "反例-无效输入", "反例-异常中断"],
  "key_inputs": ["输入1", "输入2"],
  "expected_behaviors": ["正常行为", "异常行为"]
}}
```

**模型选择**：`gpt-4o-mini`

#### 节点 2：recall_knowledge（知识召回）

与 TestPointAgent 的召回逻辑相同，但查询内容不同：

```python
query = f"测试点：{state['test_point_text']}\n类别：{state['test_point_category']}"
```

召回的可能是：历史类似测试用例、测试规范中的用例编写标准、领域特定的测试数据示例。

#### 节点 3：generate_test_cases（生成测试用例）

**Prompt 设计**：

```
你是一个专业的测试用例设计专家。请根据测试点分析和参考知识，生成测试用例。

## 测试点分析
{test_point_analysis}

## 参考知识
{knowledge_context}

## 需求上下文
{requirement_context}

## 生成要求
1. 至少生成 2 个用例：1 个正例 + 1 个反例
2. 正例覆盖正常流程和主要边界值
3. 反例覆盖无效输入和异常场景
4. 每个用例包含完整的前置条件、步骤和预期结果
5. 步骤应具体可执行，预期结果应可验证
6. 如果有参考知识，请参考其中的用例编写规范和示例

## 输出格式（JSON）
{{
  "test_cases": [
    {{
      "name": "用例名称",
      "property": "正例|反例",
      "pre_condition": "前置条件描述",
      "steps": [
        {{
          "name": "步骤名称",
          "description": "具体操作描述",
          "stepExpectedResult": "该步骤的预期结果"
        }}
      ]
    }}
  ]
}}
```

**模型选择**：`gpt-4o`

#### 节点 4：quality_check（质量校验）

**目的**：对生成的测试用例进行多维质量校验，这是与 TestPointAgent 的关键差异——用例质量直接影响测试执行效果。

**校验维度**：

| 维度 | 校验规则 | 权重 |
|------|----------|------|
| 完整性 | 每个用例是否有前置条件、步骤、预期结果 | 20% |
| 可执行性 | 步骤描述是否具体、可操作 | 20% |
| 可验证性 | 预期结果是否明确、可判定通过/失败 | 20% |
| 正反例均衡 | 是否同时包含正例和反例 | 15% |
| 步骤连贯性 | 步骤之间是否有逻辑依赖、顺序是否合理 | 15% |
| 领域相关性 | 是否结合了领域知识（如有参考知识） | 10% |

**Prompt 设计**：

```
你是一个测试用例质量评审专家。请校验以下测试用例的质量。

## 测试点
{test_point_text}

## 参考知识
{knowledge_context}

## 生成的测试用例
{test_cases_json}

## 校验维度（每项 1-5 分）
1. 完整性：每个用例是否包含前置条件、步骤、预期结果？
2. 可执行性：步骤描述是否具体可操作？能否直接执行？
3. 可验证性：预期结果是否明确？能否判定通过/失败？
4. 正反例均衡：是否同时包含正例和反例？比例是否合理？
5. 步骤连贯性：步骤之间逻辑是否连贯？顺序是否合理？
6. 领域相关性：是否结合了领域知识和测试规范？

## 输出格式（JSON）
{{
  "scores": {{
    "completeness": 4,
    "executability": 3,
    "verifiability": 4,
    "balance": 5,
    "coherence": 4,
    "domain_relevance": 3
  }},
  "average_score": 3.8,
  "passed": true,
  "issues": [
    "反例缺少对空值输入的测试",
    "步骤2的描述不够具体"
  ],
  "suggestions": [
    "增加空值输入的反例",
    "步骤2应明确操作的具体参数"
  ]
}}
```

**通过标准**：`average_score >= 3.5` 且 `executability >= 3` 且 `verifiability >= 3`

**模型选择**：`gpt-4o-mini`

#### 节点 5：self_correct（自我修正）

**目的**：根据质量校验反馈修正测试用例，仅在校验未通过时执行。

**条件执行**：`quality_result["passed"] == False` 且 `retry_count < max_retries`

**Prompt 设计**：

```
你是一个专业的测试用例设计专家。请根据质量校验反馈修正以下测试用例。

## 测试点
{test_point_text}

## 当前测试用例
{test_cases_json}

## 质量校验反馈
- 评分：{average_score}/5
- 问题：{issues}
- 建议：{suggestions}

## 修正要求
1. 针对校验指出的问题逐一修正
2. 确保每个步骤描述具体可操作
3. 确保预期结果明确可验证
4. 补充缺失的正例或反例
5. 保持用例总数在 2-4 个

## 输出格式（与生成步骤相同）
{{
  "test_cases": [
    {{
      "name": "用例名称",
      "property": "正例|反例",
      "pre_condition": "前置条件描述",
      "steps": [
        {{
          "name": "步骤名称",
          "description": "具体操作描述",
          "stepExpectedResult": "该步骤的预期结果"
        }}
      ]
    }}
  ]
}}
```

**模型选择**：`gpt-4o`

### 5.3 图结构

```python
def build_test_case_agent() -> CompiledGraph:
    graph = StateGraph(TestCaseState)

    graph.add_node("analyze_test_point", analyze_test_point)
    graph.add_node("recall_knowledge", recall_knowledge)
    graph.add_node("generate_test_cases", generate_test_cases)
    graph.add_node("quality_check", quality_check)
    graph.add_node("self_correct", self_correct)
    graph.add_node("output", output_test_cases)

    graph.set_entry_point("analyze_test_point")
    graph.add_edge("analyze_test_point", "recall_knowledge")
    graph.add_edge("recall_knowledge", "generate_test_cases")
    graph.add_edge("generate_test_cases", "quality_check")

    graph.add_conditional_edges(
        "quality_check",
        should_correct,
        {
            "correct": "self_correct",
            "output": "output",
        }
    )
    graph.add_edge("self_correct", "quality_check")  # 回到校验
    graph.add_edge("output", END)

    return graph.compile()
```

---

## 6. 编排层设计

### 6.1 TestDesignOrchestrator

替代原有的 `_run_generation` 方法，统一编排两个 Agent 的执行：

```python
class TestDesignOrchestrator:
    def __init__(self, llm_client: LLMClient, rag_service: RAGService):
        self.test_point_agent = build_test_point_agent(llm_client, rag_service)
        self.test_case_agent = build_test_case_agent(llm_client, rag_service)

    async def run(
        self,
        db: AsyncSession,
        task_id: str,
        requirement_id: str,
        use_knowledge_base: bool,
    ) -> None:
        # 1. 查询所有拆分需求
        split_reqs = await self._get_split_requirements(db, requirement_id)
        total = len(split_reqs)

        # 2. 逐个处理拆分需求
        for i, sr in enumerate(split_reqs):
            # 更新进度
            progress = int((i / total) * 90)
            await self._update_progress(db, task_id, progress, f"正在生成测试点：{sr.text[:20]}...")

            # 3. 调用 TestPointAgent
            tp_result = await self.test_point_agent.ainvoke({
                "requirement_text": sr.text,
                "use_knowledge_base": use_knowledge_base,
                "retry_count": 0,
                "max_retries": 2,
            })

            # 4. 持久化测试点并逐个生成用例
            for tp_item in tp_result["final_test_points"]:
                tp = await self._save_test_point(db, sr.id, tp_item)

                # 更新进度
                await self._update_progress(db, task_id, progress + 5, f"正在生成用例：{tp.text[:20]}...")

                # 5. 调用 TestCaseAgent
                tc_result = await self.test_case_agent.ainvoke({
                    "test_point_text": tp_item["text"],
                    "test_point_category": tp_item.get("category", ""),
                    "requirement_context": sr.text,
                    "use_knowledge_base": use_knowledge_base,
                    "retry_count": 0,
                    "max_retries": 2,
                })

                # 6. 持久化测试用例
                for tc_item in tc_result["final_test_cases"]:
                    await self._save_test_case(db, tp.id, tc_item)

        # 7. 完成任务
        await self._update_progress(db, task_id, 100, "生成完成")
```

### 6.2 与现有代码的集成点

| 现有代码 | 变更 |
|----------|------|
| `TestDesignService._run_generation` | 替换为调用 `TestDesignOrchestrator.run` |
| `TestDesignService._generate_test_points_for_split_req` | 删除，由 TestPointAgent 替代 |
| `TestDesignService._generate_test_cases_for_point` | 删除，由 TestCaseAgent 替代 |
| `KnowledgeBaseService.test_recall` | 新增 `recall_and_rerank` 方法供 RAG Service 调用 |
| `TestDesignService.http_client` | 替换为 `LLMClient` 封装 |

---

## 7. 目录结构

```
backend/app/
├── ai/                              # AI 编排层（新增）
│   ├── __init__.py
│   ├── llm_client.py                # LLM 客户端封装
│   ├── rag_service.py               # RAG 检索服务
│   ├── prompts.py                   # Prompt 模板集中管理
│   ├── agents/                      # Agent 定义
│   │   ├── __init__.py
│   │   ├── test_point_agent.py      # TestPointAgent
│   │   └── test_case_agent.py       # TestCaseAgent
│   └── orchestrator.py              # 编排器
├── services/
│   ├── test_design.py               # 修改：调用编排器
│   └── knowledge_base.py            # 修改：新增 recall_and_rerank
└── ...
```

---

## 8. 成本与性能优化

### 8.1 模型选择策略

| 步骤 | 模型 | 原因 |
|------|------|------|
| 需求分析 | gpt-4o-mini | 分析任务不需要最强推理 |
| 知识召回 | 无 LLM 调用 | Milvus 向量搜索 |
| 知识重排序 | gpt-4o-mini | 简单排序任务 |
| 测试点生成 | gpt-4o | 核心生成，需要高质量 |
| 自我评审 | gpt-4o-mini | 评审是相对简单的判断任务 |
| 测试点优化 | gpt-4o | 核心生成 |
| 用例分析 | gpt-4o-mini | 分析任务 |
| 用例生成 | gpt-4o | 核心生成 |
| 质量校验 | gpt-4o-mini | 校验是判断任务 |
| 用例修正 | gpt-4o | 核心生成 |

### 8.2 Token 消耗估算

**单个拆分需求的处理流程**（假设需求文本 200 字）：

| 步骤 | 输入 Token | 输出 Token | 模型 | 相对成本 |
|------|-----------|-----------|------|----------|
| 需求分析 | ~500 | ~300 | mini | 低 |
| 知识召回 | 0 | 0 | - | 无 |
| 知识重排序 | ~1000 | ~50 | mini | 低 |
| 测试点生成 | ~800 | ~500 | gpt-4o | 中 |
| 自我评审 | ~600 | ~200 | mini | 低 |
| 测试点优化（50%概率） | ~800 | ~500 | gpt-4o | 中 |
| 用例分析×5 | ~300×5 | ~200×5 | mini | 低 |
| 用例生成×5 | ~600×5 | ~800×5 | gpt-4o | 高 |
| 质量校验×5 | ~500×5 | ~200×5 | mini | 低 |
| 用例修正×5（50%概率） | ~600×5 | ~800×5 | gpt-4o | 高 |

**总计**：约 10K-15K Token/拆分需求，其中 gpt-4o 占约 70%

**对比原方案**：原方案每个拆分需求约 1K Token（仅 2 次 LLM 调用），新方案成本约为原方案的 10 倍，但质量显著提升。

### 8.3 优化措施

1. **缓存需求分析结果**：同一需求的多个测试点共享需求分析
2. **批量生成用例**：将同一测试点的多个用例在一次 LLM 调用中生成
3. **跳过评审**：如果首次生成评分已达标，跳过优化步骤
4. **知识召回去重**：同一需求下的多个测试点共享知识召回结果
5. **配置化模型选择**：允许用户在配置中选择使用 gpt-4o-mini 替代 gpt-4o（降低成本）

---

## 9. 错误处理与降级策略

### 9.1 LLM 调用失败

| 场景 | 处理策略 |
|------|----------|
| API 超时 | 指数退避重试 3 次 |
| Rate Limit | 等待 `retry-after` 时间后重试 |
| JSON 解析失败 | 尝试正则提取 JSON，仍失败则使用结构化输出重试 1 次 |
| 所有重试耗尽 | 降级到简化 prompt 单轮生成，仍失败则使用硬编码回退 |

### 9.2 知识库不可用

| 场景 | 处理策略 |
|------|----------|
| Milvus 连接失败 | 跳过知识召回步骤，仅基于需求文本生成 |
| 召回结果为空 | 记录日志，继续生成（无知识增强） |
| 重排序失败 | 使用原始向量搜索结果，跳过重排序 |

### 9.3 Agent 执行超时

| 场景 | 处理策略 |
|------|----------|
| 单个 Agent 执行超过 60s | 中断当前 Agent，使用已有中间结果输出 |
| 整体任务超过 10min | 标记任务失败，保存已完成的部分结果 |

---

## 10. 可观测性

### 10.1 执行日志

每个 Agent 步骤记录结构化日志：

```python
{
    "timestamp": "2025-01-01T12:00:00",
    "task_id": "task-xxx",
    "agent": "TestPointAgent",
    "node": "generate_test_points",
    "split_requirement_id": "sr-xxx",
    "input_tokens": 800,
    "output_tokens": 500,
    "model": "gpt-4o",
    "duration_ms": 3200,
    "status": "success"
}
```

### 10.2 质量追踪

记录每次生成的评审/校验结果，用于后续分析 Agent 效果：

```python
{
    "task_id": "task-xxx",
    "agent": "TestCaseAgent",
    "test_point_id": "tp-xxx",
    "quality_scores": {"completeness": 4, "executability": 3, ...},
    "average_score": 3.8,
    "retry_count": 1,
    "final_passed": true
}
```

---

## 11. 实施计划

### 阶段一：基础设施（前置依赖）

| 序号 | 任务 | 说明 |
|------|------|------|
| 1 | 实现 LLMClient | 封装 OpenAI API，支持 JSON Mode、重试、模型选择 |
| 2 | 实现 RAGService | 封装知识库召回 + LLM 重排序 |
| 3 | 实现 PromptTemplates | 集中管理所有 Prompt 模板 |
| 4 | 安装 LangGraph | `pip install langgraph` |

### 阶段二：TestPointAgent

| 序号 | 任务 | 说明 |
|------|------|------|
| 5 | 定义 TestPointState | TypedDict 状态定义 |
| 6 | 实现 analyze_requirement 节点 | 需求分析 |
| 7 | 实现 recall_knowledge 节点 | 知识库召回 |
| 8 | 实现 generate_test_points 节点 | 测试点生成 |
| 9 | 实现 self_review 节点 | 自我评审 |
| 10 | 实现 refine_points 节点 | 优化测试点 |
| 11 | 构建 StateGraph | 组装图结构 |
| 12 | 单元测试 | 验证各节点和整体流程 |

### 阶段三：TestCaseAgent

| 序号 | 任务 | 说明 |
|------|------|------|
| 13 | 定义 TestCaseState | TypedDict 状态定义 |
| 14 | 实现 analyze_test_point 节点 | 测试点分析 |
| 15 | 实现 recall_knowledge 节点 | 知识库召回 |
| 16 | 实现 generate_test_cases 节点 | 用例生成 |
| 17 | 实现 quality_check 节点 | 质量校验 |
| 18 | 实现 self_correct 节点 | 自我修正 |
| 19 | 构建 StateGraph | 组装图结构 |
| 20 | 单元测试 | 验证各节点和整体流程 |

### 阶段四：编排与集成

| 序号 | 任务 | 说明 |
|------|------|------|
| 21 | 实现 TestDesignOrchestrator | 编排两个 Agent |
| 22 | 修改 TestDesignService | 替换原有生成逻辑 |
| 23 | 修改 KnowledgeBaseService | 新增 recall_and_rerank |
| 24 | 端到端测试 | 完整流程验证 |
| 25 | 性能测试 | Token 消耗和耗时评估 |

---

## 12. 与原方案的对比

| 维度 | 原方案 | 新方案（Agent） |
|------|--------|----------------|
| LLM 调用次数 | 2 次/拆分需求 | 8-15 次/拆分需求 |
| 知识库集成 | 无 | RAG 召回 + 重排序 |
| 需求分析 | 无 | 结构化分析（功能点、约束、边界） |
| 质量校验 | 无 | 多维度自动校验 |
| 自我修正 | 无 | 最多 2 轮迭代优化 |
| 输出格式 | 行文本/正则提取 JSON | JSON Mode 结构化输出 |
| 失败回退 | 硬编码通用内容 | 降级到简化 prompt → 硬编码 |
| 可观测性 | 无 | 结构化日志 + 质量追踪 |
| 生成耗时 | ~2s/拆分需求 | ~15-30s/拆分需求 |
| Token 成本 | ~1K/拆分需求 | ~10-15K/拆分需求 |
| 用例质量 | 通用、缺乏领域性 | 专业、有领域知识、经过校验 |
