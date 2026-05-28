import json
from typing import TypedDict, Optional, List, Dict

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
