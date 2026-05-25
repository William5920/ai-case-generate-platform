from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.explore import StartExploreRequest, SendExploreMessageRequest
from app.services.explore_service import explore_service

router = APIRouter(prefix="/explore", tags=["需求探索"])


@router.post("/start", summary="开始AI探索")
async def start_explore(
    req: StartExploreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await explore_service.start_explore(
            db, user_id,
            requirement_id=req.requirementId,
            template_id=req.templateId,
            raw_content=req.rawContent,
            file_id=req.fileId
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.post("/chat", summary="发送探索消息")
async def send_explore_message(
    req: SendExploreMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await explore_service.send_explore_message(
            db, user_id,
            requirement_id=req.requirementId,
            message=req.message,
            dimension_key=req.dimensionKey,
            session_id=req.sessionId
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.get("/{requirement_id}/history", summary="获取探索历史")
async def get_explore_history(
    requirement_id: str,
    sessionId: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    data = await explore_service.get_explore_history(db, requirement_id, sessionId)
    return {"code": 200, "message": "success", "data": data}


@router.get("/status/{session_id}", summary="获取探索状态")
async def get_explore_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    data = await explore_service.get_explore_status(db, session_id)
    if not data:
        return {"code": 404, "message": "探索会话不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}
