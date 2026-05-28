from typing import List, Dict, Optional, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.db_models import SplitRequirement, TestPoint, TestCase, Requirement
from app.agents.llm_client import LLMClient
from app.agents.rag_service import RAGService
from app.agents.test_point_agent import run_test_point_agent
from app.agents.test_case_agent import run_test_case_agent
from app.services.knowledge_base import KnowledgeBaseService


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
            if progress_callback:
                await progress_callback(100, "无需生成: 没有拆分需求")
            await db.execute(
                update(Requirement)
                .where(Requirement.id == requirement_id)
                .values(status="completed")
            )
            await db.commit()
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
