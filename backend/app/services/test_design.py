import uuid
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, func, and_, or_
from sqlalchemy.orm import selectinload
import httpx
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from app.core.config import settings
from app.models.db_models import Requirement, SplitRequirement, TestPoint, TestCase, AISession, AIMessage, Task
from app.models.test_design import (
    RequirementListItem, RequirementListResponse,
    ImportRequirementRequest, ImportRequirementResponse,
    MindMapNode, MindMapNodeData,
    TestPointCreate, TestPointUpdate, TestPointResponse,
    TestCaseCreate, TestCaseUpdate, TestCaseResponse, TestCaseStep,
    AIAdjustStart, AIAdjustApply, AIAdjustApplyResponse,
    GenerateResponse, TaskStatusResponse,
    ResponseModel
)


class TestDesignService:
    def __init__(self):
        self.tasks: Dict[str, asyncio.Task] = {}
        self.http_client = httpx.AsyncClient(
            base_url=settings.OPENAI_BASE_URL,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            timeout=60.0
        )

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
        
        filters = []
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
            status_text_map = {"pending": "待生成", "generating": "生成中", "completed": "已完成"}
            items.append(RequirementListItem(
                id=req.id,
                title=req.title,
                status=req.status,
                statusText=status_text_map.get(req.status, req.status),
                date=req.updated_at.strftime("%Y-%m-%d %H:%M") if req.updated_at else "",
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
                data=MindMapNodeData(text="", _level="root", _status="pending"),
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
                            text=tc.text,
                            _level="testCase",
                            _caseProperty=tc.case_property,
                            _source=tc.source,
                            note=note_html
                        ),
                        children=[]
                    ))
                tp_children.append(MindMapNode(
                    data=MindMapNodeData(
                        text=tp.text,
                        _level="testPoint",
                        _status=tp.status,
                        _source=tp.source,
                        _marked=tp.marked
                    ),
                    children=case_children
                ))
            children.append(MindMapNode(
                data=MindMapNodeData(
                    text=sr.text,
                    _level="requirement",
                    _status=sr.status
                ),
                children=tp_children
            ))
        
        return MindMapNode(
            data=MindMapNodeData(
                text=requirement.title,
                _level="root",
                _status=requirement.status
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
        
        system_prompt = self._build_ai_adjust_prompt(data.nodeType, data.markedNodeIds or [])
        ai_message = AIMessage(session_id=session.id, role="system", content=system_prompt)
        db.add(ai_message)
        await db.commit()
        
        return {"sessionId": session.id, "message": "AI调整会话已创建"}

    def _build_ai_adjust_prompt(self, node_type: str, marked_node_ids: List[str]) -> str:
        if node_type == "requirement":
            return (
                "你是一个专业的测试设计专家。用户将对需求进行AI调整，"
                "生成或调整测试点。标记保留的测试点不会被删除或修改。"
                "请根据用户的需求描述，生成高质量的测试点。"
            )
        else:
            return (
                "你是一个专业的测试设计专家。用户将对测试点进行AI调整，"
                "生成或调整测试用例。标记保留的测试用例不会被删除或修改。"
                "请根据测试点描述，生成高质量的测试用例（包含正例和反例）。"
            )

    async def send_ai_message(self, db: AsyncSession, session_id: str, content: str) -> Dict[str, Any]:
        user_msg = AIMessage(session_id=session_id, role="user", content=content)
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
            response = await self.http_client.post(
                "/chat/completions",
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": api_messages,
                    "temperature": 0.7
                }
            )
            response_data = response.json()
            ai_content = response_data["choices"][0]["message"]["content"]
        except Exception as e:
            ai_content = f"AI服务暂时不可用，请稍后重试。错误: {str(e)}"
        
        assistant_msg = AIMessage(session_id=session_id, role="assistant", content=ai_content)
        db.add(assistant_msg)
        await db.commit()
        
        return {"role": "assistant", "content": ai_content}

    async def get_ai_messages(self, db: AsyncSession, session_id: str) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(AIMessage).where(AIMessage.session_id == session_id).order_by(AIMessage.created_at)
        )
        messages = result.scalars().all()
        return [{"role": msg.role, "content": msg.content, "createdAt": msg.created_at.isoformat()} for msg in messages]

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
