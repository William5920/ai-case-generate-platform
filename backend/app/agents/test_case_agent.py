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
