from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.split import (
    ExecuteSplitRequest, UpdateSplitRequest, AddSplitRequest, ConfirmAndTestRequest
)
from app.services.split_service import split_service

router = APIRouter(prefix="/splits", tags=["需求拆分"])


@router.post("/execute", summary="执行需求拆分")
async def execute_split(
    req: ExecuteSplitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await split_service.execute_split(
            db, user_id,
            requirement_id=req.requirementId,
            standardized_content=req.standardizedContent
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.get("/{requirement_id}", summary="获取拆分列表")
async def get_split_list(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await split_service.get_split_list(db, user_id, requirement_id)
    if not data:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.put("/{requirement_id}/{split_id}", summary="更新拆分项")
async def update_split(
    requirement_id: str,
    split_id: str,
    req: UpdateSplitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await split_service.update_split(
        db, user_id, requirement_id, split_id,
        content=req.content, order=req.order
    )
    if not data:
        return {"code": 404, "message": "拆分项不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.post("/{requirement_id}", summary="新增拆分项")
async def add_split(
    requirement_id: str,
    req: AddSplitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await split_service.add_split(
        db, user_id, requirement_id,
        content=req.content, order=req.order
    )
    if not data:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.delete("/{requirement_id}/{split_id}", summary="删除拆分项")
async def delete_split(
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


@router.post("/confirm-and-test", summary="确认拆分并生成测试")
async def confirm_and_test(
    req: ConfirmAndTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await split_service.confirm_and_test(
            db, user_id,
            requirement_id=req.requirementId,
            title=req.title,
            split_requirements=req.splitRequirements,
            standardized_content=req.standardizedContent,
            template_id=req.templateId
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}
