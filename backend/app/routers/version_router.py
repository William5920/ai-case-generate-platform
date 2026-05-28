from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.version import VersionListData, VersionDetailData, VersionDiffData, RestoreVersionData
from app.services.version_service import version_service

router = APIRouter(prefix="/versions", tags=["版本管理"])


@router.get("/{requirement_id}", summary="获取版本列表")
async def get_version_list(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await version_service.get_version_list(db, user_id, requirement_id)
    if not data:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.get("/{requirement_id}/{version_id}", summary="获取版本详情")
async def get_version_detail(
    requirement_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await version_service.get_version_detail(db, user_id, requirement_id, version_id)
    if not data:
        return {"code": 404, "message": "版本不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.post("/{requirement_id}/{version_id}/restore", summary="恢复版本")
async def restore_version(
    requirement_id: str,
    version_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await version_service.restore_version(db, user_id, requirement_id, version_id)
    if not data:
        return {"code": 404, "message": "版本不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.get("/{requirement_id}/diff", summary="获取版本差异")
async def get_version_diff(
    requirement_id: str,
    fromVersionId: str = Query(...),
    toVersionId: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await version_service.get_version_diff(
        db, user_id, requirement_id, fromVersionId, toVersionId
    )
    if not data:
        return {"code": 404, "message": "版本不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}
