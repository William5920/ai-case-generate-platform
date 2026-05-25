# 智能体（Agent）实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于设计文档实现 LangGraph 驱动的 TestPointAgent 和 TestCaseAgent，集成知识库 RAG，实现多步推理、质量校验和自我修正的完整智能体流程。

**Architecture:** 使用 LangGraph StateGraph 构建 TestPointAgent（分析→召回→生成→评审→修正）和 TestCaseAgent（分析→召回→生成→校验→修正），由 TestDesignOrchestrator 编排替代原有 `_run_generation`。共享 LLMClient、RAGService、PromptTemplates 基础设施。

**Tech Stack:** Python 3.11, LangGraph, langchain-core, httpx (OpenAI API), Milvus (pymilvus), FastAPI, SQLAlchemy

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `backend/requirements.txt` | 修改 | 新增 langgraph 依赖 |
| `backend/app/core/config.py` | 修改 | 新增模型配置项 |
| `backend/app/agents/__init__.py` | 创建 | 包初始化，导出核心类 |
| `backend/app/agents/llm_client.py` | 创建 | LLM Client 封装 |
| `backend/app/agents/rag_service.py` | 创建 | RAG 服务（封装 KnowledgeBaseService） |
| `backend/app/agents/prompts.py` | 创建 | Prompt 模板集中管理 |
| `backend/app/agents/test_point_agent.py` | 创建 | TestPointAgent (LangGraph) |
| `backend/app/agents/test_case_agent.py` | 创建 | TestCaseAgent (LangGraph) |
| `backend/app/agents/orchestrator.py` | 创建 | TestDesignOrchestrator 编排层 |
| `backend/app/services/test_design.py` | 修改 | 替换 `_run_generation` 使用 Orchestrator |

---

## Task 1: 依赖与配置更新

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/core/config.py`

- [ ] **Step 1.1: 更新 requirements.txt**

在文件末尾添加：

```
langgraph>=0.2.0
langchain-core>=0.3.0
```

- [ ] **Step 1.2: 更新 config.py**

在 Settings 类中新增模型配置项，替换单一 OPENAI_MODEL：

```python
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "智能测试用例平台"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:3000"]
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_NAME: str = "knowledge_base"
    UPLOAD_DIR: str = "./uploads"

    DATABASE_URL: str = "mysql+aiomysql://root:root123456@127.0.0.1:3306/ai_case_platform?charset=utf8mb4"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MODEL_ANALYZE: str = "gpt-4o-mini"
    OPENAI_MODEL_GENERATE: str = "gpt-4o"
    OPENAI_MAX_RETRIES: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

- [ ] **Step 1.3: 安装新依赖**

Run: `cd d:\github\ai-case-generate-platform\backend && pip install langgraph>=0.2.0 langchain-core>=0.3.0`

---

## Task 2: LLM Client 封装

**Files:**
- Create: `backend/app/agents/llm_client.py`

- [ ] **Step 2.1: 创建 LLM Client**

```python
import json
import asyncio
from typing import List, Dict, Optional
import httpx
from app.core.config import settings


class LLMClient:
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            base_url=settings.OPENAI_BASE_URL,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            timeout=120.0
        )
        self.max_retries = settings.OPENAI_MAX_RETRIES

    async def chat(
        self,
        messages: List[Dict],
        model: str = None,
        temperature: float = 0.7,
        response_format: Optional[Dict] = None,
        max_tokens: int = 4096,
    ) -> str:
        model = model or settings.OPENAI_MODEL
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        for attempt in range(self.max_retries):
            try:
                response = await self.http_client.post("/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
                    continue
                raise
            except (httpx.RequestError, KeyError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt
                await asyncio.sleep(wait)
        raise RuntimeError("LLM调用失败：超过最大重试次数")

    async def chat_with_schema(
        self,
        messages: List[Dict],
        schema_description: str,
        model: str = None,
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ) -> Dict:
        system_msg = messages[0] if messages and messages[0].get("role") == "system" else {"role": "system", "content": ""}
        if messages and messages[0].get("role") == "system":
            remaining = messages[1:]
        else:
            remaining = messages

        enhanced_system = {
            "role": "system",
            "content": system_msg["content"] + "\n\n你必须以JSON格式输出，遵循以下结构：\n" + schema_description
        }
        all_messages = [enhanced_system] + remaining

        content = await self.chat(
            messages=all_messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"LLM输出无法解析为JSON: {content[:200]}")

    async def close(self):
        await self.http_client.aclose()
```

---

## Task 3: RAG Service 封装

**Files:**
- Create: `backend/app/agents/rag_service.py`

- [ ] **Step 3.1: 创建 RAG Service**

```python
from typing import List, Optional
from dataclasses import dataclass
from app.services.knowledge_base import KnowledgeBaseService
from app.agents.llm_client import LLMClient
from app.core.config import settings


@dataclass
class RecallResult:
    content: str
    score: float
    document_id: str
    chunk_id: int


class RAGService:
    def __init__(self, kb_service: KnowledgeBaseService, llm_client: LLMClient):
        self.kb_service = kb_service
        self.llm_client = llm_client

    async def recall(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> List[RecallResult]:
        try:
            raw_results = self.kb_service.test_recall(
                query,
                params=None
            )
            results = []
            for r in raw_results:
                score = r.get("score", 0)
                if score >= threshold:
                    results.append(RecallResult(
                        content=r.get("content", ""),
                        score=score,
                        document_id=r.get("document_id", ""),
                        chunk_id=r.get("chunk_id", 0),
                    ))
            return results[:top_k]
        except Exception:
            return []

    async def recall_and_rerank(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
        final_k: int = 3,
    ) -> List[RecallResult]:
        results = await self.recall(query, top_k=top_k, threshold=threshold)
        if not results:
            return []

        if len(results) <= final_k:
            return results

        reranked = await self._rerank_with_llm(query, results)
        return reranked[:final_k]

    async def _rerank_with_llm(self, query: str, results: List[RecallResult]) -> List[RecallResult]:
        numbered = []
        for i, r in enumerate(results, 1):
            numbered.append(f"{i}. {r.content[:300]}")

        prompt = (
            "你是一个知识检索专家。请根据查询问题，对以下检索结果按相关性从高到低重新排序。\n"
            "只返回排序后的编号列表，用逗号分隔。\n\n"
            f"查询问题：{query}\n\n"
            f"检索结果：\n" + "\n".join(numbered) + "\n\n排序结果："
        )

        try:
            content = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                model=settings.OPENAI_MODEL_ANALYZE,
                temperature=0.1,
                max_tokens=100,
            )
            indices = [int(x.strip()) for x in content.strip().split(",") if x.strip().isdigit()]
            reranked = []
            for idx in indices:
                if 1 <= idx <= len(results):
                    reranked.append(results[idx - 1])
            for r in results:
                if r not in reranked:
                    reranked.append(r)
            return reranked
        except Exception:
            return results
```

---

## Task 4: Prompt 模板管理

**Files:**
- Create: `backend/app/agents/prompts.py`

- [ ] **Step 4.1: 创建 Prompt 模板**

```python
class PromptTemplates:

    TEST_POINT_ANALYZE = """你是一个专业的测试分析专家。请分析以下需求，提取出关键信息。

需求文本：
{requirement_text}

请从以下维度分析：
1. 核心功能点：该需求要实现什么功能？
2. 输入输出：涉及哪些输入和预期输出？
3. 约束条件：有哪些业务规则、限制条件？
4. 边界条件：有哪些边界值、极端情况需要考虑？
5. 关联依赖：是否依赖其他功能或外部系统？
6. 异常场景：可能出现的异常或错误情况？

请以JSON格式输出分析结果。"""

    TEST_POINT_ANALYZE_SCHEMA = """{
  "core_functions": ["功能1", "功能2"],
  "inputs_outputs": [{"input": "xxx", "output": "xxx"}],
  "constraints": ["约束1", "约束2"],
  "boundary_conditions": ["边界1", "边界2"],
  "dependencies": ["依赖1"],
  "exception_scenarios": ["异常1", "异常2"]
}"""

    TEST_POINT_GENERATE = """你是一个专业的测试设计专家。请根据以下需求分析和参考知识，生成测试点。

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
5. 如果有参考知识，请结合参考知识中的测试规范和领域经验"""

    TEST_POINT_GENERATE_SCHEMA = """{
  "test_points": [
    {
      "text": "测试点名称",
      "category": "功能验证|边界条件|异常处理|兼容性|性能|安全",
      "rationale": "为什么需要这个测试点（简述）"
    }
  ]
}"""

    TEST_POINT_REVIEW = """你是一个测试质量评审专家。请评审以下测试点列表的质量。

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
5. 领域性：是否结合了领域知识（如有参考知识）？"""

    TEST_POINT_REVIEW_SCHEMA = """{
  "scores": {
    "completeness": 4,
    "independence": 5,
    "testability": 4,
    "standardization": 3,
    "domain_relevance": 4
  },
  "average_score": 4.0,
  "passed": true,
  "issues": [
    "缺少对并发场景的测试点"
  ],
  "suggestions": [
    "增加并发场景的测试点"
  ]
}"""

    TEST_POINT_REFINE = """你是一个专业的测试设计专家。请根据评审反馈优化以下测试点。

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
4. 保持测试点总数在 3-7 个"""

    TEST_POINT_REFINE_SCHEMA = """{
  "test_points": [
    {
      "text": "测试点名称",
      "category": "功能验证|边界条件|异常处理|兼容性|性能|安全",
      "rationale": "为什么需要这个测试点"
    }
  ]
}"""

    TEST_CASE_ANALYZE = """你是一个专业的测试用例设计专家。请分析以下测试点，确定用例设计方向。

## 需求上下文
{requirement_context}

## 测试点
- 名称：{test_point_text}
- 类别：{test_point_category}

请分析：
1. 测试意图：这个测试点要验证什么？
2. 需要的用例类型：需要哪些正例和反例？
3. 关键输入：测试需要哪些输入数据？
4. 预期行为：正常和异常情况下系统应如何响应？"""

    TEST_CASE_ANALYZE_SCHEMA = """{
  "test_intent": "测试意图描述",
  "case_types_needed": ["正例-正常流程", "正例-边界值", "反例-无效输入", "反例-异常中断"],
  "key_inputs": ["输入1", "输入2"],
  "expected_behaviors": ["正常行为", "异常行为"]
}"""

    TEST_CASE_GENERATE = """你是一个专业的测试用例设计专家。请根据测试点分析和参考知识，生成测试用例。

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
6. 如果有参考知识，请参考其中的用例编写规范和示例"""

    TEST_CASE_GENERATE_SCHEMA = """{
  "test_cases": [
    {
      "name": "用例名称",
      "property": "正例|反例",
      "pre_condition": "前置条件描述",
      "steps": [
        {
          "name": "步骤名称",
          "description": "具体操作描述",
          "stepExpectedResult": "该步骤的预期结果"
        }
      ]
    }
  ]
}"""

    TEST_CASE_QUALITY_CHECK = """你是一个测试用例质量校验专家。请校验以下测试用例的质量。

## 测试点
{test_point_text}

## 需求上下文
{requirement_context}

## 生成的测试用例
{test_cases_json}

## 校验维度（每项 1-5 分）
1. 完整性：每个用例是否有前置条件、步骤、预期结果？
2. 可执行性：步骤描述是否具体、可操作？
3. 可验证性：预期结果是否明确、可判定通过/失败？
4. 正反例均衡：是否包含正例和反例，比例是否合理？
5. 规范性：用例命名是否规范，步骤是否有逻辑顺序？"""

    TEST_CASE_QUALITY_CHECK_SCHEMA = """{
  "scores": {
    "completeness": 4,
    "executability": 4,
    "verifiability": 5,
    "balance": 4,
    "standardization": 4
  },
  "average_score": 4.2,
  "passed": true,
  "issues": [
    "反例缺少异常中断场景"
  ],
  "suggestions": [
    "增加一个异常中断的反例用例"
  ]
}"""

    TEST_CASE_SELF_CORRECT = """你是一个专业的测试用例设计专家。请根据质量校验反馈修正以下测试用例。

## 测试点
{test_point_text}

## 需求上下文
{requirement_context}

## 当前测试用例
{test_cases_json}

## 校验反馈
- 评分：{average_score}/5
- 问题：{issues}
- 建议：{suggestions}

## 修正要求
1. 针对校验指出的问题逐一修正
2. 补充遗漏的用例类型（如缺少反例则补充反例）
3. 完善前置条件和步骤描述
4. 确保预期结果明确可验证"""

    TEST_CASE_SELF_CORRECT_SCHEMA = """{
  "test_cases": [
    {
      "name": "用例名称",
      "property": "正例|反例",
      "pre_condition": "前置条件描述",
      "steps": [
        {
          "name": "步骤名称",
          "description": "具体操作描述",
          "stepExpectedResult": "该步骤的预期结果"
        }
      ]
    }
  ]
}"""
```

---

## Task 5: TestPointAgent 实现

**Files:**
- Create: `backend/app/agents/test_point_agent.py`

- [ ] **Step 5.1: 创建 TestPointAgent**

```python
import json
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from app.agents.llm_client import LLMClient
from app.agents.rag_service import RAGService
from app.agents.prompts import PromptTemplates
from app.core.config import settings


class TestPointState(TypedDict):
    requirement_text: str
    use_knowledge_base: bool
    requirement_analysis: Optional[str]
    knowledge_context: Optional[str]
    test_points: Optional[List[Dict]]
    review_result: Optional[Dict]
    retry_count: int
    max_retries: int
    final_test_points: Optional[List[Dict]]


def build_test_point_agent(llm_client: LLMClient, rag_service: RAGService):
    templates = PromptTemplates()

    async def analyze_requirement(state: TestPointState) -> dict:
        messages = [
            {"role": "system", "content": "你是一个专业的测试分析专家，擅长从需求中提取关键测试信息。"},
            {"role": "user", "content": templates.TEST_POINT_ANALYZE.format(
                requirement_text=state["requirement_text"]
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_POINT_ANALYZE_SCHEMA,
            model=settings.OPENAI_MODEL_ANALYZE,
            temperature=0.3,
        )
        return {"requirement_analysis": json.dumps(result, ensure_ascii=False)}

    async def recall_knowledge(state: TestPointState) -> dict:
        if not state["use_knowledge_base"]:
            return {"knowledge_context": ""}

        query = state["requirement_analysis"] or state["requirement_text"]
        if isinstance(query, str):
            try:
                parsed = json.loads(query)
                core = parsed.get("core_functions", [])
                query = " ".join(core) if core else state["requirement_text"]
            except (json.JSONDecodeError, AttributeError):
                query = state["requirement_text"]

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

    async def generate_test_points(state: TestPointState) -> dict:
        knowledge = state.get("knowledge_context") or "无"
        messages = [
            {"role": "system", "content": "你是一个专业的测试设计专家，擅长生成高质量的测试点。"},
            {"role": "user", "content": templates.TEST_POINT_GENERATE.format(
                requirement_analysis=state.get("requirement_analysis", ""),
                knowledge_context=knowledge,
                requirement_text=state["requirement_text"],
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_POINT_GENERATE_SCHEMA,
            model=settings.OPENAI_MODEL_GENERATE,
            temperature=0.7,
        )
        return {"test_points": result.get("test_points", [])}

    async def self_review(state: TestPointState) -> dict:
        test_points_json = json.dumps(state.get("test_points", []), ensure_ascii=False, indent=2)
        messages = [
            {"role": "system", "content": "你是一个测试质量评审专家，请严格评审测试点质量。"},
            {"role": "user", "content": templates.TEST_POINT_REVIEW.format(
                requirement_text=state["requirement_text"],
                requirement_analysis=state.get("requirement_analysis", ""),
                test_points_json=test_points_json,
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_POINT_REVIEW_SCHEMA,
            model=settings.OPENAI_MODEL_ANALYZE,
            temperature=0.3,
        )

        avg = result.get("average_score", 0)
        issues = result.get("issues", [])
        has_severe = any("缺少" in str(issue) for issue in issues)
        passed = avg >= 3.5 and not has_severe
        result["passed"] = passed

        return {"review_result": result}

    async def refine_points(state: TestPointState) -> dict:
        review = state.get("review_result", {})
        test_points_json = json.dumps(state.get("test_points", []), ensure_ascii=False, indent=2)
        messages = [
            {"role": "system", "content": "你是一个专业的测试设计专家，请根据反馈优化测试点。"},
            {"role": "user", "content": templates.TEST_POINT_REFINE.format(
                requirement_text=state["requirement_text"],
                test_points_json=test_points_json,
                average_score=review.get("average_score", 0),
                issues=", ".join(str(i) for i in review.get("issues", [])),
                suggestions=", ".join(str(s) for s in review.get("suggestions", [])),
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_POINT_REFINE_SCHEMA,
            model=settings.OPENAI_MODEL_GENERATE,
            temperature=0.7,
        )
        return {
            "test_points": result.get("test_points", []),
            "retry_count": state.get("retry_count", 0) + 1,
        }

    async def output_test_points(state: TestPointState) -> dict:
        return {"final_test_points": state.get("test_points", [])}

    def should_refine(state: TestPointState) -> str:
        review = state.get("review_result", {})
        retry = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 2)

        if review.get("passed", False) or retry >= max_retries:
            return "output"
        return "refine"

    graph = StateGraph(TestPointState)

    graph.add_node("analyze_requirement", analyze_requirement)
    graph.add_node("recall_knowledge", recall_knowledge)
    graph.add_node("generate_test_points", generate_test_points)
    graph.add_node("self_review", self_review)
    graph.add_node("refine_points", refine_points)
    graph.add_node("output", output_test_points)

    graph.add_edge(START, "analyze_requirement")
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
    graph.add_edge("refine_points", "self_review")
    graph.add_edge("output", END)

    return graph.compile()


async def run_test_point_agent(
    requirement_text: str,
    use_knowledge_base: bool,
    llm_client: LLMClient,
    rag_service: RAGService,
    max_retries: int = 2,
) -> List[Dict]:
    agent = build_test_point_agent(llm_client, rag_service)
    initial_state = {
        "requirement_text": requirement_text,
        "use_knowledge_base": use_knowledge_base,
        "requirement_analysis": None,
        "knowledge_context": None,
        "test_points": None,
        "review_result": None,
        "retry_count": 0,
        "max_retries": max_retries,
        "final_test_points": None,
    }
    result = await agent.ainvoke(initial_state)
    return result.get("final_test_points", [])
```

---

## Task 6: TestCaseAgent 实现

**Files:**
- Create: `backend/app/agents/test_case_agent.py`

- [ ] **Step 6.1: 创建 TestCaseAgent**

```python
import json
from typing import TypedDict, Optional, List, Dict

from langgraph.graph import StateGraph, START, END

from app.agents.llm_client import LLMClient
from app.agents.rag_service import RAGService
from app.agents.prompts import PromptTemplates
from app.core.config import settings


class TestCaseState(TypedDict):
    test_point_text: str
    test_point_category: str
    requirement_context: str
    use_knowledge_base: bool
    knowledge_context: Optional[str]
    test_point_analysis: Optional[str]
    test_cases: Optional[List[Dict]]
    quality_result: Optional[Dict]
    retry_count: int
    max_retries: int
    final_test_cases: Optional[List[Dict]]


def build_test_case_agent(llm_client: LLMClient, rag_service: RAGService):
    templates = PromptTemplates()

    async def analyze_test_point(state: TestCaseState) -> dict:
        messages = [
            {"role": "system", "content": "你是一个专业的测试用例设计专家，擅长分析测试点并确定用例设计方向。"},
            {"role": "user", "content": templates.TEST_CASE_ANALYZE.format(
                requirement_context=state["requirement_context"],
                test_point_text=state["test_point_text"],
                test_point_category=state["test_point_category"],
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_CASE_ANALYZE_SCHEMA,
            model=settings.OPENAI_MODEL_ANALYZE,
            temperature=0.3,
        )
        return {"test_point_analysis": json.dumps(result, ensure_ascii=False)}

    async def recall_knowledge(state: TestCaseState) -> dict:
        if not state["use_knowledge_base"]:
            return {"knowledge_context": ""}

        query = f"测试点：{state['test_point_text']}\n类别：{state['test_point_category']}"
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

    async def generate_test_cases(state: TestCaseState) -> dict:
        knowledge = state.get("knowledge_context") or "无"
        messages = [
            {"role": "system", "content": "你是一个专业的测试用例设计专家，擅长生成高质量、可执行的测试用例。"},
            {"role": "user", "content": templates.TEST_CASE_GENERATE.format(
                test_point_analysis=state.get("test_point_analysis", ""),
                knowledge_context=knowledge,
                requirement_context=state["requirement_context"],
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_CASE_GENERATE_SCHEMA,
            model=settings.OPENAI_MODEL_GENERATE,
            temperature=0.7,
        )
        return {"test_cases": result.get("test_cases", [])}

    async def quality_check(state: TestCaseState) -> dict:
        test_cases_json = json.dumps(state.get("test_cases", []), ensure_ascii=False, indent=2)
        messages = [
            {"role": "system", "content": "你是一个测试用例质量校验专家，请严格校验用例质量。"},
            {"role": "user", "content": templates.TEST_CASE_QUALITY_CHECK.format(
                test_point_text=state["test_point_text"],
                requirement_context=state["requirement_context"],
                test_cases_json=test_cases_json,
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_CASE_QUALITY_CHECK_SCHEMA,
            model=settings.OPENAI_MODEL_ANALYZE,
            temperature=0.3,
        )

        avg = result.get("average_score", 0)
        issues = result.get("issues", [])
        has_severe = any("缺少" in str(issue) or "无" in str(issue) for issue in issues)
        passed = avg >= 3.5 and not has_severe
        result["passed"] = passed

        return {"quality_result": result}

    async def self_correct(state: TestCaseState) -> dict:
        quality = state.get("quality_result", {})
        test_cases_json = json.dumps(state.get("test_cases", []), ensure_ascii=False, indent=2)
        messages = [
            {"role": "system", "content": "你是一个专业的测试用例设计专家，请根据反馈修正测试用例。"},
            {"role": "user", "content": templates.TEST_CASE_SELF_CORRECT.format(
                test_point_text=state["test_point_text"],
                requirement_context=state["requirement_context"],
                test_cases_json=test_cases_json,
                average_score=quality.get("average_score", 0),
                issues=", ".join(str(i) for i in quality.get("issues", [])),
                suggestions=", ".join(str(s) for s in quality.get("suggestions", [])),
            )}
        ]
        result = await llm_client.chat_with_schema(
            messages=messages,
            schema_description=templates.TEST_CASE_SELF_CORRECT_SCHEMA,
            model=settings.OPENAI_MODEL_GENERATE,
            temperature=0.7,
        )
        return {
            "test_cases": result.get("test_cases", []),
            "retry_count": state.get("retry_count", 0) + 1,
        }

    async def output_test_cases(state: TestCaseState) -> dict:
        return {"final_test_cases": state.get("test_cases", [])}

    def should_correct(state: TestCaseState) -> str:
        quality = state.get("quality_result", {})
        retry = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 2)

        if quality.get("passed", False) or retry >= max_retries:
            return "output"
        return "correct"

    graph = StateGraph(TestCaseState)

    graph.add_node("analyze_test_point", analyze_test_point)
    graph.add_node("recall_knowledge", recall_knowledge)
    graph.add_node("generate_test_cases", generate_test_cases)
    graph.add_node("quality_check", quality_check)
    graph.add_node("self_correct", self_correct)
    graph.add_node("output", output_test_cases)

    graph.add_edge(START, "analyze_test_point")
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
    graph.add_edge("self_correct", "quality_check")
    graph.add_edge("output", END)

    return graph.compile()


async def run_test_case_agent(
    test_point_text: str,
    test_point_category: str,
    requirement_context: str,
    use_knowledge_base: bool,
    llm_client: LLMClient,
    rag_service: RAGService,
    max_retries: int = 2,
) -> List[Dict]:
    agent = build_test_case_agent(llm_client, rag_service)
    initial_state = {
        "test_point_text": test_point_text,
        "test_point_category": test_point_category,
        "requirement_context": requirement_context,
        "use_knowledge_base": use_knowledge_base,
        "knowledge_context": None,
        "test_point_analysis": None,
        "test_cases": None,
        "quality_result": None,
        "retry_count": 0,
        "max_retries": max_retries,
        "final_test_cases": None,
    }
    result = await agent.ainvoke(initial_state)
    return result.get("final_test_cases", [])
```

---

## Task 7: Orchestrator 编排层

**Files:**
- Create: `backend/app/agents/orchestrator.py`

- [ ] **Step 7.1: 创建 Orchestrator**

```python
import json
from typing import List, Dict, Optional, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.db_models import SplitRequirement, TestPoint, TestCase, Requirement, Task
from app.agents.llm_client import LLMClient
from app.agents.rag_service import RAGService
from app.agents.test_point_agent import run_test_point_agent
from app.agents.test_case_agent import run_test_case_agent
from app.services.knowledge_base import KnowledgeBaseService
from app.core.config import settings


ProgressCallback = Callable[[int, str], Awaitable[None]]


class TestDesignOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.kb_service = KnowledgeBaseService()
        self.rag_service = RAGService(self.kb_service, self.llm_client)

    async def run(
        self,
        db: AsyncSession,
        requirement_id: str,
        use_knowledge_base: bool,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        split_reqs = result.scalars().all()
        total = len(split_reqs)

        if total == 0:
            return

        for i, sr in enumerate(split_reqs):
            progress = int((i / total) * 100)
            if progress_callback:
                await progress_callback(progress, f"正在生成测试点：{sr.text[:20]}...")

            test_points_data = await run_test_point_agent(
                requirement_text=sr.text,
                use_knowledge_base=use_knowledge_base,
                llm_client=self.llm_client,
                rag_service=self.rag_service,
            )

            if not test_points_data:
                test_points_data = [
                    {"text": "功能验证", "category": "功能验证", "rationale": "默认测试点"},
                    {"text": "边界条件验证", "category": "边界条件", "rationale": "默认测试点"},
                    {"text": "异常处理验证", "category": "异常处理", "rationale": "默认测试点"},
                ]

            for tp_data in test_points_data:
                tp = TestPoint(
                    split_requirement_id=sr.id,
                    text=tp_data.get("text", "未命名测试点"),
                    description=tp_data.get("rationale", ""),
                    source="AI",
                    status="completed",
                )
                db.add(tp)
                await db.commit()
                await db.refresh(tp)

                test_cases_data = await run_test_case_agent(
                    test_point_text=tp.text,
                    test_point_category=tp_data.get("category", "功能验证"),
                    requirement_context=sr.text,
                    use_knowledge_base=use_knowledge_base,
                    llm_client=self.llm_client,
                    rag_service=self.rag_service,
                )

                if not test_cases_data:
                    test_cases_data = [
                        {
                            "name": f"{tp.text}-正例",
                            "property": "正例",
                            "pre_condition": "系统正常运行",
                            "steps": [{"name": "执行操作", "description": "按正常流程执行", "stepExpectedResult": "操作成功"}],
                        },
                        {
                            "name": f"{tp.text}-反例",
                            "property": "反例",
                            "pre_condition": "系统正常运行",
                            "steps": [{"name": "异常操作", "description": "输入异常数据", "stepExpectedResult": "系统提示错误"}],
                        },
                    ]

                for case_data in test_cases_data:
                    steps = case_data.get("steps", [])
                    tc = TestCase(
                        test_point_id=tp.id,
                        text=case_data.get("name", "未命名用例"),
                        case_property=case_data.get("property", "正例"),
                        pre_condition=case_data.get("pre_condition", ""),
                        steps=steps,
                        source="AI",
                    )
                    db.add(tc)
                    await db.commit()

        if progress_callback:
            await progress_callback(100, "生成完成")

        await db.execute(
            update(Requirement)
            .where(Requirement.id == requirement_id)
            .values(status="completed")
        )
        await db.commit()

    async def close(self):
        await self.llm_client.close()
```

---

## Task 8: 包初始化与集成

**Files:**
- Create: `backend/app/agents/__init__.py`
- Modify: `backend/app/services/test_design.py`

- [ ] **Step 8.1: 创建 `__init__.py`**

```python
from app.agents.llm_client import LLMClient
from app.agents.rag_service import RAGService
from app.agents.orchestrator import TestDesignOrchestrator

__all__ = ["LLMClient", "RAGService", "TestDesignOrchestrator"]
```

- [ ] **Step 8.2: 修改 `test_design.py` 的 `_run_generation` 方法**

在 `test_design.py` 文件中，替换 `_run_generation` 方法，使用 `TestDesignOrchestrator`：

找到 `_run_generation` 方法，将内部逻辑替换为：

```python
    async def _run_generation(self, task_id: str, requirement_id: str, use_knowledge_base: bool):
        from app.agents.orchestrator import TestDesignOrchestrator

        orchestrator = TestDesignOrchestrator()
        async with AsyncSessionLocal() as db:
            try:
                await db.execute(
                    update(Task).where(Task.id == task_id).values(status="running", progress=5, progress_text="正在分析需求结构...")
                )
                await db.commit()

                async def progress_callback(progress: int, text: str):
                    await db.execute(
                        update(Task).where(Task.id == task_id).values(progress=progress, progress_text=text)
                    )
                    await db.commit()

                await orchestrator.run(
                    db=db,
                    requirement_id=requirement_id,
                    use_knowledge_base=use_knowledge_base,
                    progress_callback=progress_callback,
                )

                await db.execute(
                    update(Task).where(Task.id == task_id).values(
                        status="completed",
                        progress=100,
                        progress_text="生成完成"
                    )
                )
                await db.commit()

            except Exception as e:
                await db.execute(
                    update(Task).where(Task.id == task_id).values(
                        status="failed",
                        progress_text=f"生成失败: {str(e)}"
                    )
                )
                await db.commit()
            finally:
                await orchestrator.close()
```

同时删除不再使用的 `_generate_test_points_for_split_req` 和 `_generate_test_cases_for_point` 方法。

---

## Task 9: 验证与测试

- [ ] **Step 9.1: 验证导入**

Run: `cd d:\github\ai-case-generate-platform\backend && python -c "from app.agents import TestDesignOrchestrator; print('Import OK')"`

- [ ] **Step 9.2: 验证 LangGraph 图构建**

Run: `cd d:\github\ai-case-generate-platform\backend && python -c "from app.agents.test_point_agent import build_test_point_agent; from app.agents.llm_client import LLMClient; from app.agents.rag_service import RAGService; from app.services.knowledge_base import KnowledgeBaseService; kb = KnowledgeBaseService(); llm = LLMClient(); rag = RAGService(kb, llm); agent = build_test_point_agent(llm, rag); print('TestPointAgent graph built OK')"`

- [ ] **Step 9.3: 启动服务验证**

Run: `cd d:\github\ai-case-generate-platform\backend && python -m uvicorn app.main:app --reload --port 8000`

验证 http://localhost:8000/docs 可访问，所有接口正常。

---

## Spec Coverage Check

| 设计文档章节 | 实现任务 | 状态 |
|-------------|---------|------|
| 3.1 LLM Client | Task 2 | ✅ |
| 3.2 RAG Service | Task 3 | ✅ |
| 3.3 Prompt 模板 | Task 4 | ✅ |
| 4 TestPointAgent | Task 5 | ✅ |
| 5 TestCaseAgent | Task 6 | ✅ |
| 2.1 TestDesignOrchestrator | Task 7 | ✅ |
| 集成到现有服务 | Task 8 | ✅ |
| 依赖与配置 | Task 1 | ✅ |
