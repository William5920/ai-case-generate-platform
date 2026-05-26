import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models.db_models import Requirement, ExploreMessage
from app.agents.llm_client import LLMClient
from app.agents.prompts import PromptTemplates
from app.services.template_service import template_service
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class ExploreService:

    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)

    async def _call_llm(self, messages, temperature=0.7, max_tokens=4096):
        if not self._llm_available:
            logger.warning("LLM call skipped: API key not configured")
            return None
        try:
            return await self._llm_client.chat(messages=messages, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.warning(f"LLM call failed: {type(e).__name__}: {e}")
            return None

    async def _call_llm_with_schema(self, messages, schema_description, temperature=0.7, max_tokens=4096):
        if not self._llm_available:
            logger.warning("LLM call with schema skipped: API key not configured")
            return None
        try:
            return await self._llm_client.chat_with_schema(messages=messages, schema_description=schema_description, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.warning(f"LLM call with schema failed: {type(e).__name__}: {e}")
            return None

    async def start_explore(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        template_id: str,
        raw_content: Optional[str] = None,
        file_id: Optional[str] = None
    ) -> dict:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        if file_id and not raw_content:
            from app.services.file_service import file_service
            raw_content = await file_service.parse_file_content(db, file_id)
            if raw_content:
                requirement.raw_content = raw_content

        dimensions = template_service.get_template_dimensions(template_id)
        if not dimensions:
            raise ValueError("模板不存在")

        requirement.status = "exploring"
        requirement.template_id = template_id
        requirement.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(requirement)

        first_dimension = dimensions[0]
        prompt = PromptTemplates.EXPLORE_START.format(
            raw_content=raw_content or requirement.raw_content or "",
            template_name=template_service.get_template_detail(template_id)["name"],
            dimension_label=first_dimension["label"],
            dimension_question=first_dimension["question"]
        )

        ai_content = await self._call_llm(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        if not ai_content:
            ai_content = f"您好！我已了解您的需求，让我们来深入了解「{first_dimension['label']}」方面的信息。{first_dimension['question']}"

        session_id = f"exp-{uuid.uuid4().hex[:8]}"
        msg_id = f"em-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        explore_message = ExploreMessage(
            id=msg_id,
            requirement_id=requirement_id,
            role="assistant",
            content=ai_content,
            dimension_key=first_dimension["key"],
            dimension_label=first_dimension["label"],
            quick_replies=[],
            replied=False,
            created_at=now
        )
        db.add(explore_message)
        await db.commit()

        return {
            "sessionId": session_id,
            "requirementId": requirement_id,
            "templateId": template_id,
            "totalDimensions": len(dimensions),
            "exploredDimensions": [],
            "understandingScore": 0,
            "firstQuestion": {
                "dimensionKey": first_dimension["key"],
                "dimensionLabel": first_dimension["label"],
                "content": ai_content
            },
            "status": "active"
        }

    async def send_explore_message(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        message: str,
        dimension_key: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> dict:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        now = datetime.utcnow()

        user_msg_id = f"em-{uuid.uuid4().hex[:8]}"
        user_message = ExploreMessage(
            id=user_msg_id,
            requirement_id=requirement_id,
            role="user",
            content=message,
            dimension_key=dimension_key,
            dimension_label=None,
            quick_replies=[],
            replied=False,
            created_at=now
        )
        db.add(user_message)

        if dimension_key:
            prev_ai_msg_result = await db.execute(
                select(ExploreMessage).where(
                    and_(
                        ExploreMessage.requirement_id == requirement_id,
                        ExploreMessage.role == "assistant",
                        ExploreMessage.dimension_key == dimension_key
                    )
                ).order_by(ExploreMessage.created_at.desc()).limit(1)
            )
            prev_ai_msg = prev_ai_msg_result.scalar_one_or_none()
            if prev_ai_msg and not prev_ai_msg.replied:
                prev_ai_msg.replied = True

        await db.commit()
        await db.refresh(requirement)

        dimensions = template_service.get_template_dimensions(requirement.template_id)
        explored_keys = await self._get_explored_dimensions(db, requirement_id)
        if dimension_key and dimension_key not in explored_keys:
            explored_keys.append(dimension_key)

        explore_data = requirement.explore_data or []
        if dimension_key:
            dim_label = ""
            for d in dimensions:
                if d["key"] == dimension_key:
                    dim_label = d["label"]
                    break
            explore_data = [e for e in explore_data if e.get("dimensionKey") != dimension_key]
            explore_data.append({
                "dimensionKey": dimension_key,
                "dimensionLabel": dim_label,
                "content": message
            })
            requirement.explore_data = explore_data

        total_dimensions = len(dimensions)
        understanding_score = self._calculate_understanding_score(
            explored_keys, total_dimensions, message
        )
        can_generate = understanding_score >= 80 or len(explored_keys) >= total_dimensions

        next_dimension = None
        for d in dimensions:
            if d["key"] not in explored_keys:
                next_dimension = d
                break

        if next_dimension:
            explore_data_text = self._format_explore_data(explore_data)
            current_dim = None
            for d in dimensions:
                if d["key"] == dimension_key:
                    current_dim = d
                    break

            prompt = PromptTemplates.EXPLORE_CHAT.format(
                raw_content=requirement.raw_content or "",
                explore_data=explore_data_text,
                dimension_label=current_dim["label"] if current_dim else "",
                dimension_key=dimension_key or "",
                dimension_question=current_dim["question"] if current_dim else "",
                user_message=message,
                next_dimension_label=next_dimension["label"],
                next_dimension_key=next_dimension["key"],
                next_dimension_question=next_dimension["question"]
            )

            ai_result = await self._call_llm_with_schema(
                messages=[{"role": "user", "content": prompt}],
                schema_description=PromptTemplates.EXPLORE_CHAT_SCHEMA,
                temperature=0.7
            )

            if not ai_result:
                ai_content = f"感谢您的回答！接下来让我们了解「{next_dimension['label']}」方面的信息。{next_dimension['question']}"
                ai_type = "question"
                next_dim_key = next_dimension["key"]
                next_dim_label = next_dimension["label"]
                quick_replies = next_dimension.get("quick_replies", [])
            else:
                ai_content = ai_result.get("content", "")
                ai_type = ai_result.get("type", "question")
                next_dim_key = ai_result.get("dimension_key", next_dimension["key"])
                next_dim_label = ai_result.get("dimension_label", next_dimension["label"])
                quick_replies = ai_result.get("quick_replies", [])
        else:
            ai_content = "感谢您的详细回答！我已经对需求有了充分的理解，现在可以为您生成标准化文档了。您也可以继续补充其他维度的信息，或者点击「生成文档」按钮开始生成。"
            ai_type = "summary"
            next_dim_key = None
            next_dim_label = None
            quick_replies = []

        ai_msg_id = f"em-{uuid.uuid4().hex[:8]}"
        ai_message = ExploreMessage(
            id=ai_msg_id,
            requirement_id=requirement_id,
            role="assistant",
            content=ai_content,
            dimension_key=next_dim_key,
            dimension_label=next_dim_label,
            quick_replies=quick_replies,
            replied=False,
            created_at=datetime.utcnow()
        )
        db.add(ai_message)

        requirement.updated_at = datetime.utcnow()
        await db.commit()

        return {
            "messageId": ai_msg_id,
            "role": "assistant",
            "content": ai_content,
            "type": ai_type,
            "dimensionKey": next_dim_key,
            "dimensionLabel": next_dim_label,
            "exploredDimensions": explored_keys,
            "totalDimensions": total_dimensions,
            "understandingScore": understanding_score,
            "canGenerate": can_generate,
            "createdAt": ai_message.created_at.isoformat() + "Z"
        }

    async def get_explore_history(
        self,
        db: AsyncSession,
        requirement_id: str,
        session_id: Optional[str] = None
    ) -> dict:
        result = await db.execute(
            select(ExploreMessage)
            .where(ExploreMessage.requirement_id == requirement_id)
            .order_by(ExploreMessage.created_at.asc())
        )
        messages = result.scalars().all()

        message_items = []
        for msg in messages:
            item = {
                "messageId": msg.id,
                "role": msg.role,
                "content": msg.content,
                "createdAt": msg.created_at.isoformat() + "Z" if msg.created_at else None
            }
            if msg.role == "assistant":
                item["type"] = "question"
                item["dimensionKey"] = msg.dimension_key
                item["dimensionLabel"] = msg.dimension_label
                item["quickReplies"] = msg.quick_replies or []
                item["replied"] = msg.replied
            message_items.append(item)

        req_result = await db.execute(
            select(Requirement).where(Requirement.id == requirement_id)
        )
        requirement = req_result.scalar_one_or_none()

        dimensions = []
        total = 0
        if requirement and requirement.template_id:
            dimensions_data = template_service.get_template_dimensions(requirement.template_id)
            total = len(dimensions_data)
            explored = await self._get_explored_dimensions(db, requirement_id)
            dimensions = explored

        return {
            "sessionId": session_id or "",
            "messages": message_items,
            "exploredDimensions": dimensions,
            "totalDimensions": total,
            "understandingScore": self._calculate_understanding_score(dimensions, total) if total > 0 else 0
        }

    async def get_explore_status(
        self,
        db: AsyncSession,
        session_id: str
    ) -> Optional[dict]:
        result = await db.execute(
            select(ExploreMessage)
            .where(ExploreMessage.dimension_key.isnot(None))
            .order_by(ExploreMessage.created_at.desc())
            .limit(1)
        )
        latest_msg = result.scalar_one_or_none()
        if not latest_msg:
            return None

        requirement_id = latest_msg.requirement_id
        req_result = await db.execute(
            select(Requirement).where(Requirement.id == requirement_id)
        )
        requirement = req_result.scalar_one_or_none()
        if not requirement:
            return None

        dimensions = template_service.get_template_dimensions(requirement.template_id)
        explored = await self._get_explored_dimensions(db, requirement_id)
        total = len(dimensions)
        score = self._calculate_understanding_score(explored, total)

        explore_data = requirement.explore_data or []

        return {
            "sessionId": session_id,
            "requirementId": requirement_id,
            "templateId": requirement.template_id,
            "status": "active" if requirement.status == "exploring" else "completed",
            "totalDimensions": total,
            "exploredDimensions": explored,
            "understandingScore": score,
            "canGenerate": score >= 80 or len(explored) >= total,
            "exploreData": explore_data,
            "startedAt": requirement.created_at.isoformat() + "Z" if requirement.created_at else None,
            "updatedAt": requirement.updated_at.isoformat() + "Z" if requirement.updated_at else None
        }

    async def _get_explored_dimensions(self, db: AsyncSession, requirement_id: str) -> List[str]:
        result = await db.execute(
            select(ExploreMessage.dimension_key)
            .where(
                and_(
                    ExploreMessage.requirement_id == requirement_id,
                    ExploreMessage.role == "user",
                    ExploreMessage.dimension_key.isnot(None)
                )
            )
        )
        keys = [row[0] for row in result.all() if row[0]]
        return list(dict.fromkeys(keys))

    def _calculate_understanding_score(
        self,
        explored_keys: List[str],
        total: int,
        latest_message: str = ""
    ) -> int:
        if total == 0:
            return 0
        base_score = int((len(explored_keys) / total) * 80)
        richness_bonus = 0
        if latest_message and len(latest_message) > 50:
            richness_bonus = min(20, len(latest_message) // 10)
        return min(100, base_score + richness_bonus)

    def _format_explore_data(self, explore_data: list) -> str:
        if not explore_data:
            return "暂无"
        lines = []
        for item in explore_data:
            lines.append(f"- {item.get('dimensionLabel', '')}: {item.get('content', '')}")
        return "\n".join(lines)


explore_service = ExploreService()
