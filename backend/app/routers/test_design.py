from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.test_design import (
    ResponseModel, RequirementListResponse,
    ImportRequirementRequest, ImportRequirementResponse,
    MindMapNode,
    TestPointCreate, TestPointUpdate, TestPointMark, TestPointResponse,
    TestCaseCreate, TestCaseUpdate, TestCaseMark, TestCaseResponse,
    BatchDeleteRequest,
    AIAdjustStart, AIAdjustApply, AIAdjustApplyResponse,
    GenerateRequest, GenerateResponse, TaskStatusResponse,
    MessageCreate
)
from app.services.test_design import test_design_service

router = APIRouter()


# ========== 需求列表 ==========
@router.post("/requirements", response_model=ResponseModel)
async def import_requirement(
    data: ImportRequirementRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.import_requirement(db, data)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements", response_model=ResponseModel)
async def get_requirements(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await test_design_service.get_requirements_list(db, page, pageSize, status, keyword)
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 脑图数据 ==========
@router.get("/requirements/{requirementId}/mindmap", response_model=ResponseModel)
async def get_mindmap(
    requirementId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        data = await test_design_service.get_mindmap_data(db, requirementId)
        return ResponseModel(data=data.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 测试点管理 ==========
@router.post("/requirements/{requirementId}/test-points", response_model=ResponseModel)
async def create_test_point(
    requirementId: str,
    data: TestPointCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.create_test_point(db, requirementId, data)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/test-points/{testPointId}", response_model=ResponseModel)
async def update_test_point(
    testPointId: str,
    data: TestPointUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.update_test_point(db, testPointId, data)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/test-points/{testPointId}", response_model=ResponseModel)
async def delete_test_point(
    testPointId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.delete_test_point(db, testPointId)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-points/batch-delete", response_model=ResponseModel)
async def batch_delete_test_points(
    data: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.batch_delete_test_points(db, data.ids)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/test-points/{testPointId}/mark", response_model=ResponseModel)
async def mark_test_point(
    testPointId: str,
    data: TestPointMark,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.mark_test_point(db, testPointId, data.marked)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 测试用例管理 ==========
@router.post("/test-points/{testPointId}/test-cases", response_model=ResponseModel)
async def create_test_case(
    testPointId: str,
    data: TestCaseCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.create_test_case(db, testPointId, data)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/test-cases/{testCaseId}", response_model=ResponseModel)
async def update_test_case(
    testCaseId: str,
    data: TestCaseUpdate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.update_test_case(db, testCaseId, data)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/test-cases/{testCaseId}", response_model=ResponseModel)
async def delete_test_case(
    testCaseId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.delete_test_case(db, testCaseId)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-cases/batch-delete", response_model=ResponseModel)
async def batch_delete_test_cases(
    data: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.batch_delete_test_cases(db, data.ids)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/test-cases/{testCaseId}/mark", response_model=ResponseModel)
async def mark_test_case(
    testCaseId: str,
    data: TestCaseMark,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.mark_test_case(db, testCaseId, data.marked)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== AI调整 ==========
@router.post("/ai-adjust/sessions", response_model=ResponseModel)
async def start_ai_session(
    data: AIAdjustStart,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.start_ai_session(db, data)
        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-adjust/sessions/{sessionId}/messages", response_model=ResponseModel)
async def send_ai_message(
    sessionId: str,
    data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.send_ai_message(db, sessionId, data.content)
        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-adjust/sessions/{sessionId}/messages", response_model=ResponseModel)
async def get_ai_messages(
    sessionId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.get_ai_messages(db, sessionId)
        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-adjust/sessions/{sessionId}/apply", response_model=ResponseModel)
async def apply_ai_adjust(
    sessionId: str,
    data: AIAdjustApply,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.apply_ai_adjust(db, sessionId, data)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 异步任务 ==========
@router.post("/requirements/{requirementId}/generate", response_model=ResponseModel)
async def start_generation(
    requirementId: str,
    data: GenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.start_generation(db, requirementId, data.useKnowledgeBase or False)
        return ResponseModel(data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements/{requirementId}/task", response_model=ResponseModel)
async def get_active_task(
    requirementId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.get_active_task(db, requirementId)
        if result:
            return ResponseModel(data=result.model_dump())
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{taskId}", response_model=ResponseModel)
async def get_task_status(
    taskId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await test_design_service.get_task_status(db, taskId)
        return ResponseModel(data=result.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{taskId}/cancel", response_model=ResponseModel)
async def cancel_task(
    taskId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        await test_design_service.cancel_task(db, taskId)
        return ResponseModel(data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 导出Excel ==========
@router.get("/requirements/{requirementId}/export")
async def export_excel(
    requirementId: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        excel_bytes = await test_design_service.export_excel(db, requirementId)
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=测试用例_{requirementId}.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
