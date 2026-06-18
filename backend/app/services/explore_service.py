import uuid
import asyncio
import json
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

        effective_file_id = file_id or requirement.file_id
        if effective_file_id and not raw_content and not requirement.raw_content:
            from app.services.file_service import file_service
            try:
                raw_content = await file_service.parse_file_content(db, effective_file_id)
                if raw_content:
                    requirement.raw_content = raw_content
            except Exception as e:
                logger.warning(f"文件解析失败: {e}")

        dimensions = template_service.get_template_dimensions(template_id)
        if not dimensions:
            raise ValueError("模板不存在")

        requirement.status = "exploring"
        requirement.template_id = template_id
        requirement.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(requirement)

        raw_content_text = raw_content or requirement.raw_content or ""
        template_name = template_service.get_template_detail(template_id)["name"]

        # 构建精简的维度列表（只发 key+label，不发 question，减少 token）
        dimensions_brief = [
            {"key": d["key"], "label": d["label"]}
            for d in dimensions
        ]
        dimensions_brief_json = json.dumps(dimensions_brief, ensure_ascii=False)

        # 并行调用：1) 维度覆盖评估（轻量 JSON） 2) 首条提问（普通文本）
        coverage_prompt = PromptTemplates.EXPLORE_COVERAGE.format(
            raw_content=raw_content_text,
            template_name=template_name,
            dimensions_json=dimensions_brief_json
        )

        first_dimension = dimensions[0]
        first_question_prompt = PromptTemplates.EXPLORE_START.format(
            raw_content=raw_content_text,
            template_name=template_name,
            dimension_label=first_dimension["label"],
            dimension_question=first_dimension["question"]
        )

        coverage_task = self._call_llm_with_schema(
            messages=[{"role": "user", "content": coverage_prompt}],
            schema_description=PromptTemplates.EXPLORE_COVERAGE_SCHEMA,
            temperature=0.3
        )
        question_task = self._call_llm(
            messages=[{"role": "user", "content": first_question_prompt}],
            temperature=0.7
        )

        coverage_result, ai_content = await asyncio.gather(
            coverage_task, question_task
        )

        # 默认值（降级）
        initial_score = self._calculate_initial_understanding_score(raw_content_text, len(dimensions))
        dimension_coverage = []
        first_dim_key = first_dimension["key"]
        first_dim_label = first_dimension["label"]

        # 处理首条提问结果
        if not ai_content:
            ai_content = f"您好！我已了解您的需求，让我们来深入了解「{first_dimension['label']}」方面的信息。{first_dimension['question']}"

        # 处理维度覆盖结果
        if coverage_result:
            dimension_coverage = coverage_result.get("dimension_coverage", [])
            llm_score = coverage_result.get("initial_score")
            # 动态上限：min(95, 已覆盖维度数/总维度数 * 100)
            covered_count = sum(1 for item in dimension_coverage if isinstance(item, dict) and item.get("covered"))
            dynamic_cap = min(95, int((covered_count / len(dimensions)) * 100)) if len(dimensions) > 0 else 95
            if isinstance(llm_score, (int, float)) and 0 <= llm_score <= dynamic_cap:
                initial_score = int(llm_score)

            # 从覆盖数据中找第一个未覆盖维度，更新首条提问的维度
            uncovered = [d for d in dimensions if not any(
                c.get("key") == d["key"] and c.get("covered") for c in dimension_coverage
            )]
            if uncovered:
                first_dim_key = uncovered[0]["key"]
                first_dim_label = uncovered[0]["label"]

        # 保存维度覆盖数据到需求记录
        if dimension_coverage:
            try:
                requirement.coverage_data = dimension_coverage
            except Exception as e:
                logger.warning(f"保存 coverage_data 失败: {e}")

        # 保存初始理解度为历史最高分
        requirement.max_understanding_score = initial_score
        await db.commit()
        await db.refresh(requirement)

        # 从 coverage_data 中提取已覆盖的维度 key
        covered_dim_keys = []
        if dimension_coverage:
            covered_dim_keys = [
                item["key"] for item in dimension_coverage
                if isinstance(item, dict) and item.get("covered") and item.get("key")
            ]

        session_id = f"exp-{uuid.uuid4().hex[:8]}"
        msg_id = f"em-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        explore_message = ExploreMessage(
            id=msg_id,
            requirement_id=requirement_id,
            role="assistant",
            content=ai_content,
            dimension_key=first_dim_key,
            dimension_label=first_dim_label,
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
            "exploredDimensions": covered_dim_keys,
            "understandingScore": initial_score,
            "firstQuestion": {
                "dimensionKey": first_dim_key,
                "dimensionLabel": first_dim_label,
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

        if not requirement.raw_content and requirement.file_id:
            try:
                from app.services.file_service import file_service
                parsed = await file_service.parse_file_content(db, requirement.file_id)
                if parsed:
                    requirement.raw_content = parsed
            except Exception as e:
                logger.warning(f"send_explore_message 文件解析失败: {e}")

        dimensions = template_service.get_template_dimensions(requirement.template_id)
        explored_keys = await self._get_explored_dimensions(db, requirement_id)
        if dimension_key and dimension_key not in explored_keys:
            explored_keys.append(dimension_key)

        # 合并 coverage_data 中已覆盖的维度
        covered_from_raw = set()
        if requirement.coverage_data:
            for item in requirement.coverage_data:
                if isinstance(item, dict) and item.get("covered") and item.get("key"):
                    covered_from_raw.add(item["key"])
        all_explored = list(dict.fromkeys(explored_keys + list(covered_from_raw)))

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
            explored_keys, total_dimensions, message,
            coverage_data=requirement.coverage_data
        )
        # 保证分数不下降：取历史最高分
        if requirement.max_understanding_score is None:
            requirement.max_understanding_score = 0
        understanding_score = max(understanding_score, requirement.max_understanding_score)
        requirement.max_understanding_score = understanding_score
        can_generate = understanding_score >= 80 or len(all_explored) >= total_dimensions

        next_dimension = None
        for d in dimensions:
            if d["key"] not in all_explored:
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
                # LLM不可用时，默认推进：标记当前维度为已探索
                if dimension_key and dimension_key not in all_explored:
                    all_explored.append(dimension_key)
            else:
                ai_content = ai_result.get("content", "")
                ai_type = ai_result.get("type", "question")
                ai_dim_key = ai_result.get("dimension_key", next_dimension["key"])
                ai_dim_label = ai_result.get("dimension_label", next_dimension["label"])

                if ai_type == "followup":
                    # AI 认为用户回复不够明确，在同维度上追问
                    next_dim_key = dimension_key or ai_dim_key
                    next_dim_label = current_dim["label"] if current_dim else ai_dim_label
                    quick_replies = ai_result.get("quick_replies", [])
                elif ai_type == "summary":
                    # 用户要求直接结束探索
                    next_dim_key = None
                    next_dim_label = None
                    quick_replies = []
                else:
                    # type == "question": AI 接受了用户回复，推进到下一个维度
                    if dimension_key and dimension_key not in all_explored:
                        all_explored.append(dimension_key)
                    next_dim_key = ai_dim_key
                    next_dim_label = ai_dim_label
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

        # 基于 AI 决策后实际的 all_explored 重新计算理解度
        if total_dimensions > 0 and all_explored:
            understanding_score = self._calculate_understanding_score(
                all_explored, total_dimensions, message,
                coverage_data=requirement.coverage_data
            )
        # 保证分数不下降：取历史最高分
        max_score = requirement.max_understanding_score or 0
        understanding_score = max(understanding_score, max_score)
        requirement.max_understanding_score = max(understanding_score, max_score)
        can_generate = understanding_score >= 80 or len(all_explored) >= total_dimensions
        await db.commit()

        return {
            "messageId": ai_msg_id,
            "role": "assistant",
            "content": ai_content,
            "type": ai_type,
            "dimensionKey": next_dim_key,
            "dimensionLabel": next_dim_label,
            "exploredDimensions": all_explored,
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
        covered_from_raw = []
        if requirement and requirement.template_id:
            dimensions_data = template_service.get_template_dimensions(requirement.template_id)
            total = len(dimensions_data)
            explored = await self._get_explored_dimensions(db, requirement_id)
            # 合并 coverage_data 中已覆盖的维度
            if requirement.coverage_data:
                covered_from_raw = [
                    item["key"] for item in requirement.coverage_data
                    if isinstance(item, dict) and item.get("covered") and item.get("key")
                ]
            dimensions = list(dict.fromkeys(explored + covered_from_raw))

        score = 0
        if total > 0:
            coverage_data = requirement.coverage_data if requirement else None
            if dimensions:
                score = self._calculate_understanding_score(dimensions, total, coverage_data=coverage_data)
            else:
                raw = requirement.raw_content if requirement else ""
                score = self._calculate_initial_understanding_score(raw, total)
            # 保证不下降：取历史最高分
            max_score = requirement.max_understanding_score if requirement else 0
            if max_score is None:
                max_score = 0
            score = max(score, max_score)

        return {
            "sessionId": session_id or "",
            "messages": message_items,
            "exploredDimensions": dimensions,
            "totalDimensions": total,
            "understandingScore": score
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
        # 合并 coverage_data 中已覆盖的维度
        covered_from_raw = []
        if requirement.coverage_data:
            covered_from_raw = [
                item["key"] for item in requirement.coverage_data
                if isinstance(item, dict) and item.get("covered") and item.get("key")
            ]
        all_explored = list(dict.fromkeys(explored + covered_from_raw))
        total = len(dimensions)
        score = self._calculate_understanding_score(explored, total, coverage_data=requirement.coverage_data)
        # 保证不下降：取历史最高分
        max_score = requirement.max_understanding_score or 0
        score = max(score, max_score)

        explore_data = requirement.explore_data or []

        return {
            "sessionId": session_id,
            "requirementId": requirement_id,
            "templateId": requirement.template_id,
            "status": "active" if requirement.status == "exploring" else "completed",
            "totalDimensions": total,
            "exploredDimensions": all_explored,
            "understandingScore": score,
            "canGenerate": score >= 80 or len(all_explored) >= total,
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
        latest_message: str = "",
        coverage_data: list = None
    ) -> int:
        if total == 0:
            return 0

        # 合并 coverage_data 中已覆盖的维度
        covered_from_raw = set()
        if coverage_data:
            for item in coverage_data:
                if isinstance(item, dict) and item.get("covered") and item.get("key"):
                    covered_from_raw.add(item["key"])

        all_explored = set(explored_keys) | covered_from_raw
        base_score = int((len(all_explored) / total) * 80)

        # richness_bonus 取消息长度对应的最大值，保证分数不下降
        richness_bonus = 0
        if latest_message and len(latest_message) > 50:
            richness_bonus = min(20, len(latest_message) // 10)

        return min(100, base_score + richness_bonus)

    def _calculate_initial_understanding_score(
        self,
        raw_content: str,
        total_dimensions: int
    ) -> int:
        """
        根据原始需求内容计算初始需求理解度。
        内容越多、结构越丰富，理解度越高，但上限为50%，
        因为仍有具体的模板维度需要通过AI探索来确认。
        """
        if not raw_content or total_dimensions == 0:
            return 0

        content_len = len(raw_content)

        # 内容丰富度评分：内容越长，基础分越高
        if content_len < 50:
            richness = 5
        elif content_len < 200:
            richness = 15
        elif content_len < 500:
            richness = 35
        elif content_len < 1000:
            richness = 55
        elif content_len < 2000:
            richness = 72
        else:
            richness = 88

        # 结构丰富度加分：统计有效行数（每两行 +1，上限 7）
        lines = [l.strip() for l in raw_content.split('\n') if l.strip()]
        structure_bonus = min(7, len(lines) // 2)

        return min(95, richness + structure_bonus)

    def _format_explore_data(self, explore_data: list) -> str:
        if not explore_data:
            return "暂无"
        lines = []
        for item in explore_data:
            lines.append(f"- {item.get('dimensionLabel', '')}: {item.get('content', '')}")
        return "\n".join(lines)


explore_service = ExploreService()
