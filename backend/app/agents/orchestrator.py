from typing import List, Dict, Optional, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

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
        """保留旧方法兼容性：同时生成测试点和用例"""
        await self.run_points(db, requirement_id, use_knowledge_base, progress_callback)
        # 检查是否被中途取消
        check = await db.execute(
            select(Requirement.status).where(Requirement.id == requirement_id)
        )
        current_status = check.scalar()
        if current_status not in ("points_generated",):
            return
        await self.run_cases(db, requirement_id, use_knowledge_base, False, progress_callback)

    async def run_points(
        self,
        db: AsyncSession,
        requirement_id: str,
        use_knowledge_base: bool,
        regenerate_all: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        """仅生成测试点，不生成用例。regenerate_all=True 时先清空已有测试点及用例再重建"""
        # 如果 regenerate_all，先清理已有测试点（会级联删除用例）
        if regenerate_all:
            result = await db.execute(
                select(SplitRequirement)
                .where(SplitRequirement.requirement_id == requirement_id)
            )
            existing_srs = result.scalars().all()
            for sr in existing_srs:
                await db.execute(
                    delete(TestPoint).where(TestPoint.split_requirement_id == sr.id)
                )
            await db.commit()

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
                .values(status="points_generated")
            )
            await db.commit()
            return

        for i, sr in enumerate(split_reqs):
            progress = int((i / total) * 100)
            if progress_callback:
                await progress_callback(progress, f"正在生成测试点：{sr.text}")

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

        if progress_callback:
            await progress_callback(100, "测试点生成完成")

        await db.execute(
            update(Requirement)
            .where(Requirement.id == requirement_id)
            .values(status="points_generated")
        )
        await db.commit()

    async def run_cases(
        self,
        db: AsyncSession,
        requirement_id: str,
        use_knowledge_base: bool,
        regenerate_all: bool = False,
        progress_callback: Optional[ProgressCallback] = None,
    ) -> None:
        """生成测试用例。默认增量模式，仅对无子用例的测试点生成"""
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .options(selectinload(SplitRequirement.test_points))
        )
        split_reqs = result.scalars().all()

        # 收集所有需要生成用例的测试点
        tp_to_generate = []
        for sr in split_reqs:
            for tp in sr.test_points:
                if regenerate_all:
                    tp_to_generate.append((sr, tp))
                else:
                    # 增量模式：检查是否已有用例
                    case_count = await db.execute(
                        select(func.count(TestCase.id))
                        .where(TestCase.test_point_id == tp.id)
                    )
                    if case_count.scalar() == 0:
                        tp_to_generate.append((sr, tp))

        total = len(tp_to_generate)
        if total == 0:
            if progress_callback:
                await progress_callback(100, "所有测试点已存在用例，无需生成")
            await db.execute(
                update(Requirement)
                .where(Requirement.id == requirement_id)
                .values(status="completed")
            )
            await db.commit()
            return

        for i, (sr, tp) in enumerate(tp_to_generate):
            progress = int((i / total) * 100)
            if progress_callback:
                await progress_callback(progress, f"正在生成用例：{tp.text}")

            # 如果 regenerate_all，先清理已有用例
            if regenerate_all:
                await db.execute(
                    delete(TestCase).where(TestCase.test_point_id == tp.id)
                )

            test_cases_data = await run_test_case_agent(
                test_point_text=tp.text,
                test_point_category=tp.description or "功能验证",
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
            await progress_callback(100, "用例生成完成")

        await db.execute(
            update(Requirement)
            .where(Requirement.id == requirement_id)
            .values(status="completed")
        )
        await db.commit()

    async def close(self):
        await self.llm_client.close()
