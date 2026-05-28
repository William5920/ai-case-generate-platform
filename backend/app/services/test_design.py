import uuid
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_, or_
from sqlalchemy.orm import selectinload
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from app.core.config import settings
from app.agents.prompts import PromptTemplates
from app.models.db_models import Requirement, SplitRequirement, TestPoint, TestCase, AISession, AIMessage, Task

logger = logging.getLogger("uvicorn.error")
from app.models.test_design import (
    RequirementListItem, RequirementListResponse,
    ImportRequirementRequest, ImportRequirementResponse,
    MindMapNode, MindMapNodeData,
    TestPointCreate, TestPointUpdate, TestPointResponse,
    TestCaseCreate, TestCaseUpdate, TestCaseResponse, TestCaseStep,
    AIAdjustStart, AIAdjustApply, AIAdjustApplyResponse,
    GenerateResponse, TaskStatusResponse,
    ResponseModel,
    AdoptProposalResponse, RejectProposalResponse,
)


class TestDesignService:
    def __init__(self):
        from app.agents.llm_client import LLMClient
        self.tasks: Dict[str, asyncio.Task] = {}
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)

    # ========== 需求列表 ==========
    async def import_requirement(
        self, db: AsyncSession, data: ImportRequirementRequest
    ) -> ImportRequirementResponse:
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        requirement = Requirement(
            id=req_id,
            user_id="00000000-0000-0000-0000-000000000000",
            title=data.title,
            content=data.standardizedContent,
            status="pending",
            source="standardization",
            created_at=now,
            updated_at=now,
        )
        db.add(requirement)

        for idx, sr in enumerate(data.splitRequirements):
            if not sr.selected:
                continue
            sr_id = f"sr-{uuid.uuid4().hex[:8]}"
            split_req = SplitRequirement(
                id=sr_id,
                requirement_id=req_id,
                text=sr.content,
                status="pending",
                sort_order=idx,
                created_at=now,
            )
            db.add(split_req)

        await db.commit()

        return ImportRequirementResponse(
            id=req_id,
            title=data.title,
            status="pending",
            statusText="待生成",
            date=now.strftime("%Y-%m-%d %H:%M"),
            testPointCount=0,
            caseCount=0,
            source="standardization",
        )

    async def get_requirements_list(
        self, db: AsyncSession, page: int, pageSize: int, status: Optional[str], keyword: Optional[str]
    ) -> RequirementListResponse:
        query = select(Requirement)
        count_query = select(func.count(Requirement.id))
        
        filters = [Requirement.status.in_(["confirmed", "generating", "completed"])]
        if status:
            filters.append(Requirement.status == status)
        if keyword:
            filters.append(Requirement.title.contains(keyword))
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        query = query.order_by(Requirement.updated_at.desc())
        query = query.offset((page - 1) * pageSize).limit(pageSize)
        
        result = await db.execute(query)
        requirements = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        items = []
        for req in requirements:
            tp_count = await self._get_test_point_count(db, req.id)
            case_count = await self._get_case_count(db, req.id)
            status_text_map = {"confirmed": "待生成", "generating": "生成中", "completed": "已完成"}
            items.append(RequirementListItem(
                id=req.id,
                title=req.title,
                status=req.status,
                statusText=status_text_map.get(req.status, req.status),
                date=req.updated_at.isoformat() + "Z" if req.updated_at else "",
                testPointCount=tp_count,
                caseCount=case_count,
                source=req.source
            ))
        
        return RequirementListResponse(list=items, total=total, page=page, pageSize=pageSize)

    async def _get_test_point_count(self, db: AsyncSession, requirement_id: str) -> int:
        query = select(func.count(TestPoint.id)).join(SplitRequirement).where(
            SplitRequirement.requirement_id == requirement_id
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def _get_case_count(self, db: AsyncSession, requirement_id: str) -> int:
        query = select(func.count(TestCase.id)).join(TestPoint).join(SplitRequirement).where(
            SplitRequirement.requirement_id == requirement_id
        )
        result = await db.execute(query)
        return result.scalar() or 0

    # ========== 脑图数据 ==========
    async def get_mindmap_data(self, db: AsyncSession, requirement_id: str) -> MindMapNode:
        result = await db.execute(
            select(Requirement).where(Requirement.id == requirement_id)
        )
        requirement = result.scalar_one_or_none()
        if not requirement:
            return MindMapNode(
                data=MindMapNodeData(id="", text="", level="root", status="pending"),
                children=[]
            )
        
        sr_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .order_by(SplitRequirement.sort_order)
            .options(selectinload(SplitRequirement.test_points).selectinload(TestPoint.test_cases))
        )
        split_reqs = sr_result.scalars().all()
        
        children = []
        for sr in split_reqs:
            tp_children = []
            for tp in sr.test_points:
                case_children = []
                for tc in tp.test_cases:
                    note_html = self._build_case_note_html(tc)
                    case_children.append(MindMapNode(
                        data=MindMapNodeData(
                            id=tc.id,
                            text=tc.text,
                            level="testCase",
                            case_property=tc.case_property,
                            source=tc.source,
                            note=note_html,
                            pre_condition=tc.pre_condition,
                            steps=tc.steps,
                            marked=tc.marked
                        ),
                        children=[]
                    ))
                tp_children.append(MindMapNode(
                    data=MindMapNodeData(
                        id=tp.id,
                        text=tp.text,
                        level="testPoint",
                        status=tp.status,
                        source=tp.source,
                        marked=tp.marked,
                        description=tp.description
                    ),
                    children=case_children
                ))
            children.append(MindMapNode(
                data=MindMapNodeData(
                    id=sr.id,
                    text=sr.text,
                    level="requirement",
                    status=sr.status
                ),
                children=tp_children
            ))
        
        return MindMapNode(
            data=MindMapNodeData(
                id=requirement.id,
                text=requirement.title,
                level="root",
                status=requirement.status
            ),
            children=children
        )

    def _build_case_note_html(self, tc: TestCase) -> str:
        steps_html = ""
        if tc.steps:
            for step in tc.steps:
                steps_html += f"<div class='step'><b>{step.get('name', '')}</b>: {step.get('description', '')} → {step.get('stepExpectedResult', '')}</div>"
        return f"<div class='case-note-popover'><p><b>前置条件:</b> {tc.pre_condition or '无'}</p><p><b>步骤:</b></p>{steps_html}</div>"

    # ========== 测试点管理 ==========
    async def create_test_point(self, db: AsyncSession, requirement_id: str, data: TestPointCreate) -> TestPointResponse:
        test_point = TestPoint(
            split_requirement_id=data.requirementNodeId,
            text=data.text,
            description=data.description,
            source="人工"
        )
        db.add(test_point)
        await db.commit()
        await db.refresh(test_point)
        return TestPointResponse(id=test_point.id, text=test_point.text, _source="人工")

    async def update_test_point(self, db: AsyncSession, test_point_id: str, data: TestPointUpdate) -> TestPointResponse:
        result = await db.execute(
            update(TestPoint).where(TestPoint.id == test_point_id).values(text=data.text)
        )
        await db.commit()
        return TestPointResponse(id=test_point_id, text=data.text, _source="人工")

    async def delete_test_point(self, db: AsyncSession, test_point_id: str) -> bool:
        await db.execute(delete(TestPoint).where(TestPoint.id == test_point_id))
        await db.commit()
        return True

    async def batch_delete_test_points(self, db: AsyncSession, ids: List[str]) -> bool:
        await db.execute(delete(TestPoint).where(TestPoint.id.in_(ids)))
        await db.commit()
        return True

    async def mark_test_point(self, db: AsyncSession, test_point_id: str, marked: bool) -> bool:
        await db.execute(
            update(TestPoint).where(TestPoint.id == test_point_id).values(marked=marked)
        )
        await db.commit()
        return True

    # ========== 测试用例管理 ==========
    async def create_test_case(self, db: AsyncSession, test_point_id: str, data: TestCaseCreate) -> TestCaseResponse:
        steps = []
        if data.steps:
            steps = [step.model_dump() for step in data.steps]
        test_case = TestCase(
            test_point_id=test_point_id,
            text=data.text,
            case_property=data.caseProperty,
            pre_condition=data.preCondition,
            steps=steps,
            source="人工"
        )
        db.add(test_case)
        await db.commit()
        await db.refresh(test_case)
        return TestCaseResponse(
            id=test_case.id,
            text=test_case.text,
            caseProperty=test_case.case_property,
            preCondition=test_case.pre_condition,
            steps=data.steps
        )

    async def update_test_case(self, db: AsyncSession, test_case_id: str, data: TestCaseUpdate) -> TestCaseResponse:
        steps = []
        if data.steps:
            steps = [step.model_dump() for step in data.steps]
        await db.execute(
            update(TestCase).where(TestCase.id == test_case_id).values(
                text=data.text,
                case_property=data.caseProperty,
                pre_condition=data.preCondition,
                steps=steps
            )
        )
        await db.commit()
        return TestCaseResponse(
            id=test_case_id,
            text=data.text,
            caseProperty=data.caseProperty,
            preCondition=data.preCondition,
            steps=data.steps
        )

    async def delete_test_case(self, db: AsyncSession, test_case_id: str) -> bool:
        await db.execute(delete(TestCase).where(TestCase.id == test_case_id))
        await db.commit()
        return True

    async def batch_delete_test_cases(self, db: AsyncSession, ids: List[str]) -> bool:
        await db.execute(delete(TestCase).where(TestCase.id.in_(ids)))
        await db.commit()
        return True

    async def mark_test_case(self, db: AsyncSession, test_case_id: str, marked: bool) -> bool:
        await db.execute(
            update(TestCase).where(TestCase.id == test_case_id).values(marked=marked)
        )
        await db.commit()
        return True

    # ========== AI调整 ==========
    async def start_ai_session(self, db: AsyncSession, data: AIAdjustStart) -> Dict[str, Any]:
        session = AISession(
            requirement_id=data.requirementId,
            node_id=data.nodeId,
            node_type=data.nodeType,
            marked_node_ids=data.markedNodeIds or []
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        context_data = await self._get_ai_adjust_context(db, data)
        system_prompt = self._build_ai_adjust_prompt(data.nodeType, data.markedNodeIds or [], context_data)
        ai_message = AIMessage(session_id=session.id, role="system", content=system_prompt)
        db.add(ai_message)
        await db.commit()

        return {"sessionId": session.id, "message": "AI调整会话已创建"}

    async def _get_ai_adjust_context(self, db: AsyncSession, data: AIAdjustStart) -> Dict[str, Any]:
        if data.nodeType == "requirement":
            sr_result = await db.execute(
                select(SplitRequirement).where(SplitRequirement.id == data.nodeId)
            )
            sr = sr_result.scalar_one_or_none()
            tp_result = await db.execute(
                select(TestPoint)
                .where(TestPoint.split_requirement_id == data.nodeId)
                .order_by(TestPoint.created_at)
            )
            test_points = tp_result.scalars().all()
            return {
                "node_text": sr.text if sr else "",
                "existing_items": [{"id": tp.id, "text": tp.text, "marked": tp.marked} for tp in test_points],
                "item_label": "测试点",
            }
        else:
            tp_result = await db.execute(
                select(TestPoint).where(TestPoint.id == data.nodeId)
            )
            tp = tp_result.scalar_one_or_none()
            tc_result = await db.execute(
                select(TestCase)
                .where(TestCase.test_point_id == data.nodeId)
                .order_by(TestCase.created_at)
            )
            test_cases = tc_result.scalars().all()
            return {
                "node_text": tp.text if tp else "",
                "existing_items": [
                    {"id": tc.id, "text": tc.text, "property": tc.case_property, "marked": tc.marked}
                    for tc in test_cases
                ],
                "item_label": "测试用例",
            }

    def _build_ai_adjust_prompt(self, node_type: str, marked_node_ids: List[str], context: Dict[str, Any]) -> str:
        node_text = context.get("node_text", "")
        existing_items = context.get("existing_items", [])
        item_label = context.get("item_label", "")

        items_text = ""
        if existing_items:
            for item in existing_items:
                marker = " [标记保留]" if item.get("marked") else ""
                prop = f" [{item.get('property', '')}]" if item.get("property") else ""
                items_text += f"  - {item['text']}{prop}{marker}\n"
        else:
            items_text = "  （暂无）\n"

        if node_type == "requirement":
            return (
                "你是一个专业的测试设计专家。以下是当前需求的拆分内容和已有的测试点，"
                "请基于这些信息帮助用户调整、补充或重新生成测试点。\n"
                f"\n【当前需求拆分内容】\n{node_text}\n"
                f"\n【已有{item_label}】\n{items_text}\n"
                "【标记保留的测试点ID】\n"
                f"{', '.join(marked_node_ids) if marked_node_ids else '无'}\n"
                "\n注意：标记保留的测试点不可删除或修改其内容。"
                "请根据用户的调整要求，在保留已有有效测试点的基础上，补充或优化测试点。"
                "\n\n当你给出调整建议(type=proposal)时，必须在pending_nodes中列出所有变更："
                "\n- 新增测试点：action为add，填写text和可选的description"
                "\n- 删除测试点：action为remove，填写id为已有测试点ID（不可删除标记保留的测试点）"
                "\n- 重要：除非用户明确要求删除，否则只新增不要删除已有测试点"
            )
        else:
            return (
                "你是一个专业的测试设计专家。以下是当前测试点的内容和已有的测试用例，"
                "请基于这些信息帮助用户调整、补充或重新生成测试用例（包含正例和反例）。\n"
                f"\n【当前测试点内容】\n{node_text}\n"
                f"\n【已有{item_label}】\n{items_text}\n"
                "【标记保留的测试用例ID】\n"
                f"{', '.join(marked_node_ids) if marked_node_ids else '无'}\n"
                "\n注意：标记保留的测试用例不可删除或修改其内容。"
                "请根据用户的调整要求，在保留已有有效测试用例的基础上，补充或优化测试用例。"
                "每个测试用例需包含：用例名称、用例属性（正例/反例）、前置条件、测试步骤。"
                "\n\n当你给出调整建议(type=proposal)时，必须在pending_nodes中列出所有变更："
                "\n- 新增测试用例：action为add，填写text、case_property（正例/反例）、可选的pre_condition和steps"
                "\n- 删除测试用例：action为remove，填写id为已有测试用例ID（不可删除标记保留的测试用例）"
                "\n- 重要：除非用户明确要求删除，否则只新增不要删除已有测试用例"
            )

    async def _call_llm_with_schema(self, messages, schema_description, temperature=0.7, max_tokens=8192):
        if not self._llm_available:
            logger.warning("LLM call with schema skipped: API key not configured")
            return None
        try:
            return await self._llm_client.chat_with_schema(
                messages=messages,
                schema_description=schema_description,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.warning(f"LLM call with schema failed: {type(e).__name__}: {e}")
            return None

    async def send_ai_message(self, db: AsyncSession, session_id: str, content: str) -> Dict[str, Any]:
        user_msg = AIMessage(session_id=session_id, role="user", content=content, msg_type="text")
        db.add(user_msg)
        await db.commit()

        messages_result = await db.execute(
            select(AIMessage).where(AIMessage.session_id == session_id).order_by(AIMessage.created_at)
        )
        messages = messages_result.scalars().all()

        api_messages = []
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})

        try:
            ai_result = await self._call_llm_with_schema(
                messages=api_messages,
                schema_description=PromptTemplates.TEST_DESIGN_ADJUST_SCHEMA,
                temperature=0.7,
                max_tokens=8192
            )

            if not ai_result:
                ai_result = {
                    "content": "AI服务暂时不可用，请稍后重试。",
                    "type": "discussion",
                    "change_summary": ""
                }

            ai_content = ai_result.get("content", "")
            msg_type = ai_result.get("type", "discussion")
            change_summary = ai_result.get("change_summary") if msg_type == "proposal" else None
            pending_nodes = ai_result.get("pending_nodes") if msg_type == "proposal" else None

            pending_mindmap_data = None
            if msg_type == "proposal" and pending_nodes:
                snapshot = await self._build_mindmap_snapshot(db, session_id)
                if snapshot:
                    snapshot["_adjustNodes"] = pending_nodes
                pending_mindmap_data = snapshot

            assistant_msg = AIMessage(
                session_id=session_id, role="assistant", content=ai_content,
                msg_type=msg_type, change_summary=change_summary,
                pending_mindmap_data=pending_mindmap_data
            )
        except Exception as e:
            ai_content = f"AI服务暂时不可用，请稍后重试。错误: {str(e)}"
            assistant_msg = AIMessage(
                session_id=session_id, role="assistant", content=ai_content,
                msg_type="text"
            )

        db.add(assistant_msg)
        await db.commit()
        await db.refresh(assistant_msg)

        return {
            "id": assistant_msg.id,
            "role": "assistant",
            "content": ai_content,
            "type": assistant_msg.msg_type or "text",
            "changeSummary": assistant_msg.change_summary,
            "pendingMindMapData": assistant_msg.pending_mindmap_data,
            "timestamp": assistant_msg.created_at.isoformat() + "Z" if assistant_msg.created_at else None,
        }

    async def adopt_proposal(self, db: AsyncSession, session_id: str, message_id: str, requirement_id: str) -> AdoptProposalResponse:
        result = await db.execute(
            select(AIMessage).where(
                and_(AIMessage.id == message_id, AIMessage.session_id == session_id)
            )
        )
        msg = result.scalar_one_or_none()
        if not msg:
            raise ValueError("消息不存在")

        msg.adopted = True
        msg.rejected = False

        session_result = await db.execute(
            select(AISession).where(AISession.id == session_id)
        )
        session = session_result.scalar_one_or_none()
        await db.commit()

        if msg.pending_mindmap_data and session:
            await self._apply_mindmap_changes(
                db, session.requirement_id, session.node_id, session.node_type,
                session.marked_node_ids or [], msg.pending_mindmap_data
            )

        return AdoptProposalResponse(messageId=message_id, adopted=True)

    async def reject_proposal(self, db: AsyncSession, session_id: str, message_id: str, requirement_id: str) -> RejectProposalResponse:
        result = await db.execute(
            select(AIMessage).where(
                and_(AIMessage.id == message_id, AIMessage.session_id == session_id)
            )
        )
        msg = result.scalar_one_or_none()
        if not msg:
            raise ValueError("消息不存在")

        msg.rejected = True
        msg.adopted = False
        await db.commit()

        return RejectProposalResponse(messageId=message_id, rejected=True)

    def _extract_change_summary(self, content: str) -> Optional[str]:
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("变更摘要") or line.startswith("调整摘要") or line.startswith("变更内容"):
                return line.split("：", 1)[-1].split(":", 1)[-1].strip() if ("：" in line or ":" in line) else line
        lines = content.strip().split("\n")
        first_line = lines[0] if lines else ""
        if len(first_line) <= 120:
            return first_line
        return content[:120] + "..."

    async def _build_mindmap_snapshot(self, db: AsyncSession, session_id: str) -> Optional[Dict[str, Any]]:
        result = await db.execute(
            select(AISession).where(AISession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return None
        try:
            mindmap = await self.get_mindmap_data(db, session.requirement_id)
            return mindmap.model_dump(by_alias=True)
        except Exception:
            return None

    async def _apply_mindmap_changes(
        self, db: AsyncSession, requirement_id: str, node_id: str,
        node_type: str, marked_node_ids: List[str], pending_data: Any
    ) -> None:
        pending_nodes = pending_data.get("_adjustNodes", []) if isinstance(pending_data, dict) else []
        if not pending_nodes:
            return
        now = datetime.utcnow()
        for node in pending_nodes:
            action = node.get("action", "")
            if action == "add" and node_type == "requirement":
                tp_id = f"tp-{uuid.uuid4().hex[:8]}"
                test_point = TestPoint(
                    id=tp_id,
                    split_requirement_id=node_id,
                    text=node.get("text", ""),
                    description=node.get("description"),
                    source="AI",
                    marked=False,
                    status="pending",
                    created_at=now,
                    updated_at=now
                )
                db.add(test_point)
            elif action == "remove" and node_type == "requirement":
                target_id = node.get("id", "")
                if target_id and target_id not in marked_node_ids:
                    await db.execute(delete(TestPoint).where(TestPoint.id == target_id))
            elif action == "add" and node_type == "testPoint":
                tc_id = f"tc-{uuid.uuid4().hex[:8]}"
                steps_data = node.get("steps") or []
                test_case = TestCase(
                    id=tc_id,
                    test_point_id=node_id,
                    text=node.get("text", ""),
                    case_property=node.get("case_property", "正例"),
                    pre_condition=node.get("pre_condition"),
                    steps=steps_data,
                    source="AI",
                    marked=False,
                    created_at=now,
                    updated_at=now
                )
                db.add(test_case)
            elif action == "remove" and node_type == "testPoint":
                target_id = node.get("id", "")
                if target_id and target_id not in marked_node_ids:
                    await db.execute(delete(TestCase).where(TestCase.id == target_id))
        await db.commit()

    async def get_ai_messages(self, db: AsyncSession, session_id: str) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(AIMessage).where(AIMessage.session_id == session_id).order_by(AIMessage.created_at)
        )
        messages = result.scalars().all()
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "type": msg.msg_type or "text",
                "changeSummary": msg.change_summary,
                "pendingMindMapData": msg.pending_mindmap_data,
                "adopted": msg.adopted,
                "rejected": msg.rejected,
                "createdAt": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]

    async def apply_ai_adjust(self, db: AsyncSession, session_id: str, data: AIAdjustApply) -> AIAdjustApplyResponse:
        result = await db.execute(
            select(AISession).where(AISession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("会话不存在")
        
        await db.execute(
            update(AISession).where(AISession.id == session_id).values(status="applied")
        )
        await db.commit()
        
        return AIAdjustApplyResponse(
            adjustedMindMapData=data.currentMindMapData,
            addedCount=0,
            removedCount=0,
            preservedCount=len(data.markedTestPointTexts or [])
        )

    # ========== 异步任务 ==========
    async def start_generation(self, db: AsyncSession, requirement_id: str, use_knowledge_base: bool) -> GenerateResponse:
        await db.execute(
            update(Requirement).where(Requirement.id == requirement_id).values(status="generating")
        )
        
        task = Task(
            requirement_id=requirement_id,
            status="pending",
            progress=0,
            progress_text="准备生成...",
            use_knowledge_base=use_knowledge_base
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        asyncio.create_task(self._run_generation(task.id, requirement_id, use_knowledge_base))
        
        return GenerateResponse(taskId=task.id)

    async def _run_generation(self, task_id: str, requirement_id: str, use_knowledge_base: bool):
        from app.agents.orchestrator import TestDesignOrchestrator
        from app.core.database import AsyncSessionLocal

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
                await db.execute(
                    update(Requirement).where(Requirement.id == requirement_id).values(status="confirmed")
                )
                await db.commit()
            finally:
                await orchestrator.close()

    async def get_task_status(self, db: AsyncSession, task_id: str) -> TaskStatusResponse:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise ValueError("任务不存在")
        return TaskStatusResponse(
            taskId=task.id,
            requirementId=task.requirement_id,
            status=task.status,
            progress=task.progress,
            progressText=task.progress_text
        )

    async def get_active_task(self, db: AsyncSession, requirement_id: str) -> Optional[TaskStatusResponse]:
        result = await db.execute(
            select(Task).where(
                and_(
                    Task.requirement_id == requirement_id,
                    Task.status.in_(["pending", "running"])
                )
            ).order_by(Task.created_at.desc()).limit(1)
        )
        task = result.scalar_one_or_none()
        if not task:
            return None
        return TaskStatusResponse(
            taskId=task.id,
            requirementId=task.requirement_id,
            status=task.status,
            progress=task.progress,
            progressText=task.progress_text
        )

    async def cancel_task(self, db: AsyncSession, task_id: str) -> bool:
        await db.execute(
            update(Task).where(Task.id == task_id).values(
                status="cancelled",
                progress_text="任务已取消"
            )
        )
        await db.commit()
        return True

    # ========== Excel导出 ==========
    async def export_excel(self, db: AsyncSession, requirement_id: str) -> bytes:
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .options(selectinload(SplitRequirement.test_points).selectinload(TestPoint.test_cases))
        )
        split_reqs = result.scalars().all()
        
        wb = Workbook()
        ws = wb.active
        ws.title = "测试用例"
        
        headers = ["测试用例名称", "用例类型", "前置条件", "步骤名字", "步骤描述", "步骤预期结果"]
        ws.append(headers)
        
        header_fill = PatternFill(start_color="B8CCE4", end_color="B8CCE4", fill_type="solid")
        header_font = Font(bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        col_widths = [30, 10, 30, 20, 30, 30]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        current_row = 2
        for sr in split_reqs:
            for tp in sr.test_points:
                for tc in tp.test_cases:
                    steps = tc.steps or []
                    if not steps:
                        steps = [{"name": "", "description": "", "stepExpectedResult": ""}]
                    
                    start_row = current_row
                    for step in steps:
                        ws.append([
                            tc.text,
                            tc.case_property,
                            tc.pre_condition or "",
                            step.get("name", ""),
                            step.get("description", ""),
                            step.get("stepExpectedResult", "")
                        ])
                        current_row += 1
                    
                    if len(steps) > 1:
                        for col in [1, 2, 3]:
                            ws.merge_cells(start_row=start_row, start_column=col, end_row=current_row - 1, end_column=col)
                            cell = ws.cell(row=start_row, column=col)
                            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=6):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
        
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output.getvalue()


test_design_service = TestDesignService()
