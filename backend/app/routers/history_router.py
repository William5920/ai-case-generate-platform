from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.requirement import RequirementListQuery
from app.services.requirement_service import requirement_service

router = APIRouter(prefix="/history", tags=["历史记录"])


@router.get("", summary="获取历史记录列表")
async def get_history_list(
    pageNo: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=100),
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


@router.get("/{history_id}", summary="获取历史记录详情")
async def get_history_detail(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    data = await requirement_service.get_requirement_detail(db, user_id, history_id)
    if not data:
        return {"code": 404, "message": "记录不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}
