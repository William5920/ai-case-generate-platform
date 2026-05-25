import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import logging

from app.models.db_models import Requirement, SplitRequirement
from app.agents.llm_client import LLMClient
from app.agents.prompts import PromptTemplates
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class SplitService:

    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)

    async def _call_llm_with_schema(self, messages, schema_description, temperature=0.3, max_tokens=4096):
        if not self._llm_available:
            return None
        try:
            return await self._llm_client.chat_with_schema(messages=messages, schema_description=schema_description, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.warning(f"LLM call with schema failed: {e}")
            return None

    async def execute_split(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        standardized_content: str
    ) -> dict:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        prompt = PromptTemplates.REQUIREMENT_SPLIT.format(
            standardized_content=standardized_content
        )

        split_result = await self._call_llm_with_schema(
            messages=[{"role": "user", "content": prompt}],
            schema_description=PromptTemplates.REQUIREMENT_SPLIT_SCHEMA,
            temperature=0.3
        )

        if split_result:
            splits_data = split_result.get("splits", [])
        else:
            paragraphs = [p.strip() for p in standardized_content.split("\n\n") if p.strip()]
            splits_data = [{"content": p} for p in paragraphs[:20]]

        existing_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        existing = existing_result.scalars().all()
        for e in existing:
            await db.delete(e)

        split_items = []
        for idx, split in enumerate(splits_data):
            split_id = f"sp-{uuid.uuid4().hex[:8]}"
            split_req = SplitRequirement(
                id=split_id,
                requirement_id=requirement_id,
                content=split.get("content", ""),
                order_index=idx + 1,
                created_at=datetime.utcnow()
            )
            db.add(split_req)
            split_items.append({
                "id": split_id,
                "content": split.get("content", ""),
                "order": idx + 1
            })

        requirement.status = "split"
        requirement.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "requirementId": requirement_id,
            "splits": split_items,
            "totalCount": len(split_items)
        }

    async def get_split_list(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        split_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .order_by(SplitRequirement.order_index)
        )
        splits = split_result.scalars().all()

        split_items = [
            {"id": s.id, "content": s.content, "order": s.order_index}
            for s in splits
        ]

        return {
            "splits": split_items,
            "totalCount": len(split_items)
        }

    async def update_split(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        split_id: str,
        content: str,
        order: Optional[int] = None
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        split_result = await db.execute(
            select(SplitRequirement).where(
                and_(
                    SplitRequirement.id == split_id,
                    SplitRequirement.requirement_id == requirement_id
                )
            )
        )
        split_req = split_result.scalar_one_or_none()
        if not split_req:
            return None

        split_req.content = content
        if order is not None:
            split_req.order_index = order

        requirement.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "id": split_req.id,
            "content": split_req.content,
            "order": split_req.order_index,
            "updatedAt": requirement.updated_at.isoformat() + "Z"
        }

    async def add_split(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        content: str,
        order: Optional[int] = None
    ) -> Optional[dict]:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return None

        max_order_result = await db.execute(
            select(func.max(SplitRequirement.order_index))
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        max_order = max_order_result.scalar() or 0

        actual_order = order if order is not None else max_order + 1

        split_id = f"sp-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        split_req = SplitRequirement(
            id=split_id,
            requirement_id=requirement_id,
            content=content,
            order_index=actual_order,
            created_at=now
        )
        db.add(split_req)

        requirement.updated_at = now
        await db.commit()

        return {
            "id": split_id,
            "content": content,
            "order": actual_order,
            "createdAt": now.isoformat() + "Z"
        }

    async def delete_split(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        split_id: str
    ) -> bool:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return False

        split_result = await db.execute(
            select(SplitRequirement).where(
                and_(
                    SplitRequirement.id == split_id,
                    SplitRequirement.requirement_id == requirement_id
                )
            )
        )
        split_req = split_result.scalar_one_or_none()
        if not split_req:
            return False

        await db.delete(split_req)
        requirement.updated_at = datetime.utcnow()
        await db.commit()
        return True

    async def confirm_and_test(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        title: str,
        split_requirements: List[dict],
        standardized_content: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> dict:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        requirement.status = "confirmed"
        requirement.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "id": requirement_id,
            "title": title,
            "status": "pending",
            "statusText": "待生成",
            "date": "",
            "testPointCount": 0,
            "caseCount": 0,
            "source": "standardization",
            "mindMapData": None
        }


split_service = SplitService()
