from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.requirement import (
    CreateRequirementRequest, UpdateRequirementRequest, RequirementListQuery
)
from app.services.requirement_service import requirement_service
from app.services.file_service import file_service

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
