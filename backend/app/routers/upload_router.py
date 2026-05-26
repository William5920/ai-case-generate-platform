from fastapi import APIRouter, UploadFile, File, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.file_service import file_service

router = APIRouter(tags=["文件上传"])


@router.post("/upload", summary="上传需求文档")
async def upload_file(
    file: UploadFile = File(...),
    type: str = Query("requirement"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.id
    try:
        data = await file_service.upload_file(db, user_id, file, type)
        return {
            "success": True,
            "code": 200,
            "message": "上传成功",
            "data": data,
        }
    except ValueError as e:
        return {
            "success": False,
            "code": 400,
            "message": str(e),
            "data": None,
        }
