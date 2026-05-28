from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import json
import io
from urllib.parse import quote

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.requirement import (
    CreateRequirementRequest, UpdateRequirementRequest, RequirementListQuery
)
from app.services.requirement_service import requirement_service
from app.services.file_service import file_service
from app.services.split_service import split_service
from app.schemas.split import (
    ConfirmAndTestRequest, ExecuteSplitRequest, UpdateSplitRequest,
    AddSplitRequest
)

router = APIRouter(prefix="/requirements", tags=["需求管理"])


@router.post("", summary="创建需求")
async def create_requirement(
    req: CreateRequirementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await requirement_service.create_requirement(db, user_id, req)
    return {"code": 200, "message": "success", "data": data}


@router.get("", summary="获取需求列表")
async def get_requirement_list(
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    query = RequirementListQuery(
        pageNo=pageNo, pageSize=pageSize,
        keyword=keyword, status=status
    )
    data = await requirement_service.get_requirement_list(db, user_id, query)
    return {"code": 200, "message": "success", "data": data}


@router.get("/{requirement_id}", summary="获取需求详情")
async def get_requirement_detail(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await requirement_service.get_requirement_detail(db, user_id, requirement_id)
    if not data:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.put("/{requirement_id}", summary="更新需求")
async def update_requirement(
    requirement_id: str,
    req: UpdateRequirementRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await requirement_service.update_requirement(db, user_id, requirement_id, req)
    if not data:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.delete("/{requirement_id}", summary="删除需求")
async def delete_requirement(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    success = await requirement_service.delete_requirement(db, user_id, requirement_id)
    if not success:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": None}


@router.post("/upload", summary="上传需求文档")
async def upload_file(
    file: UploadFile = File(...),
    purpose: str = Query("requirement"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await file_service.upload_file(db, user_id, file, purpose)
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.post("/{requirement_id}/split", summary="执行需求拆分")
async def execute_split(
    requirement_id: str,
    req: ExecuteSplitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await split_service.execute_split(
            db, user_id,
            requirement_id=requirement_id,
            standardized_content=req.standardizedContent or ""
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.post("/{requirement_id}/splits", summary="手动添加拆分项")
async def add_split_requirement(
    requirement_id: str,
    req: AddSplitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await split_service.add_split(
            db, user_id,
            requirement_id=requirement_id,
            content=req.content,
            order=req.order
        )
        if not data:
            return {"code": 404, "message": "需求不存在", "data": None}
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.delete("/{requirement_id}/splits/{split_id}", summary="删除拆分项")
async def delete_split_requirement(
    requirement_id: str,
    split_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    success = await split_service.delete_split(db, user_id, requirement_id, split_id)
    if not success:
        return {"code": 404, "message": "拆分项不存在", "data": None}
    return {"code": 200, "message": "success", "data": None}


@router.get("/{requirement_id}/export", summary="导出需求文档")
async def export_requirement(
    requirement_id: str,
    format: str = Query("docx"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await requirement_service.get_requirement_detail(db, user_id, requirement_id)
        if not data:
            return {"code": 404, "message": "需求不存在", "data": None}

        raw = data.get("standardizedContent") or data.get("rawContent") or ""
        if isinstance(raw, (dict, list)):
            content = json.dumps(raw, ensure_ascii=False, indent=2)
        elif isinstance(raw, str):
            content = raw
        else:
            content = str(raw)

        filename = data.get("title", "需求") or "需求"
        filename = filename.replace("/", "_").replace("\\", "_").replace(" ", "_")

        content_bytes = content.encode("utf-8")
        stream = io.BytesIO(content_bytes)

        if format == "docx":
            return StreamingResponse(
                stream,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}.docx"}
            )
        else:
            return StreamingResponse(
                stream,
                media_type="text/markdown; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}.md"}
            )
    except Exception as e:
        logger.error(f"导出需求文档失败: {e}")
        return {"code": 500, "message": f"导出失败: {str(e)}", "data": None}


@router.post("/{requirement_id}/confirm-and-test", summary="确认拆分并生成测试")
async def confirm_and_test(
    requirement_id: str,
    req: ConfirmAndTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        actual_id = None
        if requirement_id and requirement_id != "null":
            actual_id = requirement_id
        elif req.requirementId:
            actual_id = req.requirementId

        if not actual_id:
            from app.services.requirement_service import requirement_service
            from app.schemas.requirement import CreateRequirementRequest
            create_req = CreateRequirementRequest(
                title=req.title or "未命名需求",
                inputMode="text",
                rawContent=req.standardizedContent or "",
                templateId=req.templateId
            )
            create_data = await requirement_service.create_requirement(db, user_id, create_req)
            actual_id = create_data["id"]

        data = await split_service.confirm_and_test(
            db, user_id,
            requirement_id=actual_id,
            title=req.title or "未命名需求",
            split_requirements=req.splitRequirements or [],
            standardized_content=req.standardizedContent or "",
            template_id=req.templateId
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}
