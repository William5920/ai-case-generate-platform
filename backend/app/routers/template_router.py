from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.template import TemplateListData, RecommendTemplateRequest, RecommendTemplateData
from app.services.template_service import template_service

router = APIRouter(prefix="/templates", tags=["模板管理"])


@router.get("", response_model=TemplateListData, summary="获取模板列表")
async def get_template_list():
    return template_service.get_template_list()


@router.get("/{template_id}", summary="获取模板详情")
async def get_template_detail(template_id: str):
    result = template_service.get_template_detail(template_id)
    if not result:
        return {"code": 404, "message": "模板不存在", "data": None}
    return {"code": 200, "message": "success", "data": result}


@router.post("/recommend", summary="推荐模板")
async def recommend_template(
    req: RecommendTemplateRequest,
    current_user: dict = Depends(get_current_user)
):
    result = await template_service.recommend_template(req.content, req.inputMode)
    return {"code": 200, "message": "success", "data": result}
