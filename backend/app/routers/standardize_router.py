from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.standardize import (
    StandardizeRequest, SendAdjustMessageRequest,
    AdoptProposalRequest, RejectProposalRequest, QualityScoreRequest
)
from app.models.db_models import AdjustMessage
from app.services.standardize_service import standardize_service
from app.services.quality_service import quality_service

router = APIRouter(prefix="/standardize", tags=["文档标准化"])


@router.post("", summary="生成标准化文档")
async def generate_standardized_doc(
    req: StandardizeRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.id
    try:
        requirement_id = req.requirementId
        if not requirement_id:
            from app.services.requirement_service import requirement_service
            from app.schemas.requirement import CreateRequirementRequest
            create_req = CreateRequirementRequest(
                title=req.title or "未命名需求",
                inputMode=req.inputMode or "text",
                rawContent=req.rawContent,
                fileId=req.fileId,
                templateId=req.templateId
            )
            create_data = await requirement_service.create_requirement(db, user_id, create_req)
            requirement_id = create_data["id"]

        data = await standardize_service.process_standardize(
            db, user_id,
            requirement_id=requirement_id,
            template_id=req.templateId or "user-story",
            input_mode=req.inputMode or "text",
            raw_content=req.rawContent,
            file_id=req.fileId,
            explore_data=req.exploreData
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.get("/{requirement_id}/result", summary="获取标准化结果")
async def get_standardized_result(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.id
    data = await standardize_service.get_standardized_result(db, user_id, requirement_id)
    if not data:
        return {"code": 404, "message": "需求不存在", "data": None}
    return {"code": 200, "message": "success", "data": data}


@router.post("/chat", summary="发送调整消息")
async def send_adjust_message(
    req: SendAdjustMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await standardize_service.send_adjust_message(
            db, user_id,
            requirement_id=req.requirementId,
            message=req.message,
            current_content=req.currentContent,
            template_id=req.templateId,
            context=req.context
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.get("/{requirement_id}/adjust/history", summary="获取调整历史")
async def get_adjust_history(
    requirement_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.id
    data = await standardize_service.get_adjust_history(db, user_id, requirement_id)
    return {"code": 200, "message": "success", "data": data}


@router.post("/adopt", summary="采纳调整建议")
async def adopt_proposal(
    req: AdoptProposalRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.id
    msg_result = await db.execute(
        select(AdjustMessage).where(
            and_(
                AdjustMessage.requirement_id == req.requirementId,
                AdjustMessage.role == "assistant",
                AdjustMessage.confirmed == False,
                AdjustMessage.rejected == False,
                AdjustMessage.proposal_content.isnot(None)
            )
        ).order_by(AdjustMessage.created_at.desc()).limit(1)
    )
    latest_proposal = msg_result.scalar_one_or_none()
    if not latest_proposal:
        return {"code": 404, "message": "没有可采纳的建议", "data": None}
    try:
        data = await standardize_service.adopt_proposal(
            db, user_id, latest_proposal.id, req.requirementId
        )
        return {"code": 200, "message": "success", "data": data}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.post("/reject", summary="拒绝调整建议")
async def reject_proposal(
    req: RejectProposalRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_id = current_user.id
    msg_result = await db.execute(
        select(AdjustMessage).where(
            and_(
                AdjustMessage.requirement_id == req.requirementId,
                AdjustMessage.role == "assistant",
                AdjustMessage.confirmed == False,
                AdjustMessage.rejected == False,
                AdjustMessage.proposal_content.isnot(None)
            )
        ).order_by(AdjustMessage.created_at.desc()).limit(1)
    )
    latest_proposal = msg_result.scalar_one_or_none()
    if not latest_proposal:
        return {"code": 404, "message": "没有可拒绝的建议", "data": None}
    try:
        await standardize_service.reject_proposal(
            db, user_id, latest_proposal.id, req.requirementId
        )
        return {"code": 200, "message": "success", "data": None}
    except ValueError as e:
        return {"code": 400, "message": str(e), "data": None}


@router.post("/quality-score", summary="计算质量评分")
async def calculate_quality_score(
    req: QualityScoreRequest,
    current_user=Depends(get_current_user)
):
    data = await quality_service.calculate_quality_score(
        db=None,
        requirement_id=req.requirementId,
        content=req.content,
        template_id=req.templateId
    )
    return {"code": 200, "message": "success", "data": data}
