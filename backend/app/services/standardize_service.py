import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.db_models import Requirement, AdjustMessage, DocVersion
from app.agents.llm_client import LLMClient
from app.agents.prompts import PromptTemplates
from app.services.template_service import template_service
from app.core.config import settings


class StandardizeService:

    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)

    async def _call_llm(self, messages, temperature=0.7, max_tokens=8192):
        if not self._llm_available:
            return None
        try:
            return await self._llm_client.chat(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            import logging
            logging.getLogger("uvicorn.error").warning(f"LLM call failed: {e}")
            return None

    async def _call_llm_with_schema(self, messages, schema_description, temperature=0.5, max_tokens=8192):
        if not self._llm_available:
            return None
        try:
            return await self._llm_client.chat_with_schema(
                messages=messages,
                schema_description=schema_description,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            import logging
            logging.getLogger("uvicorn.error").warning(f"LLM call with schema failed: {e}")
            return None

    async def process_standardize(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        template_id: str,
        input_mode: str,
        raw_content: Optional[str] = None,
        file_id: Optional[str] = None,
        explore_data: Optional[List[dict]] = None
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

        actual_raw_content = raw_content or requirement.raw_content or ""
        actual_explore_data = explore_data or requirement.explore_data or []

        template_detail = template_service.get_template_detail(template_id)
        if not template_detail:
            raise ValueError("模板不存在")

        template_name = template_detail["name"]
        template_sections = template_service.get_template_sections_text(template_id)
        explore_data_text = self._format_explore_data(actual_explore_data)

        prompt = PromptTemplates.STANDARDIZE_GENERATE.format(
            template_name=template_name,
            raw_content=actual_raw_content,
            explore_data=explore_data_text,
            template_sections=template_sections
        )

        standardized_content = await self._call_llm(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=8192
        )

        if not standardized_content:
            standardized_content = self._generate_fallback_content(
                template_name, template_sections, actual_raw_content, actual_explore_data
            )

        requirement.standardized_content = standardized_content
        requirement.template_id = template_id
        requirement.status = "standardized"
        if actual_explore_data:
            requirement.explore_data = actual_explore_data
        requirement.updated_at = datetime.utcnow()

        version_id = f"ver-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()
        doc_version = DocVersion(
            id=version_id,
            requirement_id=requirement_id,
            version_number=1,
            content=standardized_content,
            description="初始版本",
            created_at=now
        )
        db.add(doc_version)
        await db.commit()

        return {
            "requirementId": requirement_id,
            "standardizedContent": standardized_content,
            "templateId": template_id,
            "versionId": version_id,
            "versionNumber": 1,
            "completedAt": now.isoformat() + "Z"
        }

    async def get_standardized_result(
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

        version_result = await db.execute(
            select(DocVersion)
            .where(DocVersion.requirement_id == requirement_id)
            .order_by(DocVersion.version_number.desc())
            .limit(1)
        )
        latest_version = version_result.scalar_one_or_none()

        return {
            "requirementId": requirement_id,
            "standardizedContent": requirement.standardized_content,
            "currentVersionId": latest_version.id if latest_version else None,
            "currentVersionNumber": latest_version.version_number if latest_version else 0,
            "updatedAt": requirement.updated_at.isoformat() + "Z" if requirement.updated_at else None
        }

    async def send_adjust_message(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str,
        message: str,
        current_content: str,
        template_id: Optional[str] = None,
        context: Optional[dict] = None
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

        user_msg_id = f"am-{uuid.uuid4().hex[:8]}"
        user_message = AdjustMessage(
            id=user_msg_id,
            requirement_id=requirement_id,
            role="user",
            content=message,
            message_type="discussion",
            proposal_content=None,
            change_summary=None,
            confirmed=False,
            rejected=False,
            created_at=now
        )
        db.add(user_message)
        await db.commit()

        context_info = ""
        if context:
            quick_topic = context.get("quickTopic")
            if quick_topic:
                context_info = f"用户关注的快捷话题：{quick_topic}"

        prompt = PromptTemplates.STANDARDIZE_ADJUST.format(
            user_message=message,
            current_content=current_content,
            context_info=context_info
        )

        ai_result = await self._call_llm_with_schema(
            messages=[{"role": "user", "content": prompt}],
            schema_description=PromptTemplates.STANDARDIZE_ADJUST_SCHEMA,
            temperature=0.5,
            max_tokens=8192
        )

        if not ai_result:
            ai_result = {
                "content": "AI服务暂时不可用，请稍后重试。您也可以直接在左侧编辑区手动修改文档内容。",
                "type": "discussion",
                "pending_content": None,
                "change_summary": ""
            }

        ai_content = ai_result.get("content", "")
        ai_type = ai_result.get("type", "discussion")
        pending_content = ai_result.get("pending_content")
        change_summary = ai_result.get("change_summary", "")

        ai_msg_id = f"am-{uuid.uuid4().hex[:8]}"
        ai_message = AdjustMessage(
            id=ai_msg_id,
            requirement_id=requirement_id,
            role="assistant",
            content=ai_content,
            message_type=ai_type,
            proposal_content=pending_content,
            change_summary=change_summary,
            confirmed=False,
            rejected=False,
            created_at=datetime.utcnow()
        )
        db.add(ai_message)
        await db.commit()

        proposal = None
        if ai_type == "proposal" and pending_content:
            proposal = {
                "pendingContent": pending_content,
                "changeSummary": change_summary
            }

        return {
            "messageId": ai_msg_id,
            "role": "assistant",
            "content": ai_content,
            "type": ai_type,
            "proposal": proposal,
            "createdAt": ai_message.created_at.isoformat() + "Z"
        }

    async def get_adjust_history(
        self,
        db: AsyncSession,
        user_id: str,
        requirement_id: str
    ) -> dict:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return {"messages": []}

        msg_result = await db.execute(
            select(AdjustMessage)
            .where(AdjustMessage.requirement_id == requirement_id)
            .order_by(AdjustMessage.created_at.asc())
        )
        messages = msg_result.scalars().all()

        message_items = []
        for msg in messages:
            item = {
                "messageId": msg.id,
                "role": msg.role,
                "content": msg.content,
                "createdAt": msg.created_at.isoformat() + "Z" if msg.created_at else None
            }
            if msg.role == "assistant":
                item["type"] = msg.message_type
                if msg.proposal_content:
                    item["proposal"] = {
                        "pendingContent": msg.proposal_content,
                        "changeSummary": msg.change_summary or ""
                    }
                item["confirmed"] = msg.confirmed
                item["rejected"] = msg.rejected
            message_items.append(item)

        return {"messages": message_items}

    async def adopt_proposal(
        self,
        db: AsyncSession,
        user_id: str,
        message_id: str,
        requirement_id: str
    ) -> dict:
        result = await db.execute(
            select(Requirement).where(
                and_(Requirement.id == requirement_id, Requirement.user_id == user_id)
            )
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        msg_result = await db.execute(
            select(AdjustMessage).where(
                and_(
                    AdjustMessage.id == message_id,
                    AdjustMessage.requirement_id == requirement_id,
                    AdjustMessage.role == "assistant"
                )
            )
        )
        adjust_msg = msg_result.scalar_one_or_none()
        if not adjust_msg:
            raise ValueError("消息不存在")
        if adjust_msg.confirmed:
            raise ValueError("该建议已被采纳")
        if adjust_msg.rejected:
            raise ValueError("该建议已被拒绝")
        if not adjust_msg.proposal_content:
            raise ValueError("该消息不包含建议内容")

        new_content = adjust_msg.proposal_content
        requirement.standardized_content = new_content
        requirement.updated_at = datetime.utcnow()

        adjust_msg.confirmed = True

        version_result = await db.execute(
            select(func.max(DocVersion.version_number))
            .where(DocVersion.requirement_id == requirement_id)
        )
        max_version = version_result.scalar() or 0
        new_version_number = max_version + 1

        version_id = f"ver-{uuid.uuid4().hex[:8]}"
        doc_version = DocVersion(
            id=version_id,
            requirement_id=requirement_id,
            version_number=new_version_number,
            content=new_content,
            description=f"采纳AI建议：{adjust_msg.change_summary or '调整文档内容'}",
            created_at=datetime.utcnow()
        )
        db.add(doc_version)
        await db.commit()

        return {
            "requirementId": requirement_id,
            "newContent": new_content,
            "newVersionId": version_id,
            "newVersionNumber": new_version_number,
            "changeSummary": adjust_msg.change_summary or "采纳AI建议"
        }

    async def reject_proposal(
        self,
        db: AsyncSession,
        user_id: str,
        message_id: str,
        requirement_id: str
    ) -> None:
        msg_result = await db.execute(
            select(AdjustMessage).where(
                and_(
                    AdjustMessage.id == message_id,
                    AdjustMessage.requirement_id == requirement_id,
                    AdjustMessage.role == "assistant"
                )
            )
        )
        adjust_msg = msg_result.scalar_one_or_none()
        if not adjust_msg:
            raise ValueError("消息不存在")

        adjust_msg.rejected = True
        await db.commit()

    def _format_explore_data(self, explore_data: list) -> str:
        if not explore_data:
            return "暂无探索数据"
        lines = []
        for item in explore_data:
            lines.append(f"- {item.get('dimensionLabel', '')}: {item.get('content', '')}")
        return "\n".join(lines)

    def _generate_fallback_content(
        self,
        template_name: str,
        template_sections: str,
        raw_content: str,
        explore_data: list
    ) -> str:
        explore_text = self._format_explore_data(explore_data)
        sections = [s.strip() for s in template_sections.split("\n") if s.strip()]

        content_parts = [f"# {template_name}\n"]
        content_parts.append(f"\n## 1. 概述\n\n{raw_content}\n")

        if explore_text and explore_text != "暂无探索数据":
            content_parts.append(f"\n## 2. 需求详情\n\n{explore_text}\n")

        idx = 3
        for section in sections:
            if section in ["概述", "需求详情"]:
                continue
            content_parts.append(f"\n## {idx}. {section}\n\n> 待补充：请在此处补充{section}相关内容\n")
            idx += 1

        content_parts.append("\n---\n*本文档由模板自动生成，AI服务暂不可用，请手动补充各章节内容*\n")
        return "".join(content_parts)


standardize_service = StandardizeService()
