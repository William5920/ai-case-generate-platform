from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import os
import uuid
import shutil
import tempfile
from app.models.knowledge_base import (
    ResponseModel,
    RecallSettingsUpdate, ReprocessRequest, RecallTestRequest,
    BatchStatusRequest, UploadDocToKnowledgeBaseRequest,
)
from app.core.config import settings
from app.services.knowledge_base import KnowledgeBaseService

router = APIRouter()

knowledge_service = KnowledgeBaseService()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


class UploadDocRequest(BaseModel):
    title: str
    content: str
    templateId: Optional[str] = None
    format: str = "markdown"


# ========== 上传标准化文档到知识库 ==========
@router.post("/upload-doc", response_model=ResponseModel)
async def upload_doc(req: UploadDocRequest):
    try:
        filename = f"{req.title}.md"
        tmp_path = os.path.join(tempfile.gettempdir(), f"kb_upload_{uuid.uuid4().hex}.md")
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(req.content)

        data = knowledge_service.upload_document(
            file_path=tmp_path,
            original_filename=filename,
        )

        try:
            os.remove(tmp_path)
        except Exception:
            pass

        return ResponseModel(message="文档已上传到知识库", data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 1. 文档管理 ==========
@router.get("/documents", response_model=ResponseModel)
async def get_documents(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sortBy: str = Query("uploadTime"),
    sortOrder: str = Query("desc"),
):
    try:
        data = knowledge_service.get_documents(
            page=page, pageSize=pageSize, keyword=keyword,
            format=format, status=status, sortBy=sortBy, sortOrder=sortOrder,
        )
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}", response_model=ResponseModel)
async def get_document_detail(document_id: str):
    try:
        data = knowledge_service.get_document_detail(document_id)
        if not data:
            raise HTTPException(status_code=404, detail="文档不存在")
        return ResponseModel(data=data.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/upload", response_model=ResponseModel)
async def upload_document(
    file: UploadFile = File(...),
    overwrite: bool = Query(False),
):
    try:
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        data = knowledge_service.upload_document(
            file_path=file_path,
            original_filename=file.filename or "unknown",
            overwrite=overwrite,
        )
        return ResponseModel(message="文档上传成功，正在处理中...", data=data.model_dump())
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        error_msg = str(e)
        code_map = {
            "文件大小超过限制": 4001,
            "文档数量已达上限": 4002,
            "存储空间不足": 4003,
            "不支持的文件格式": 4004,
        }
        code = 400
        for key, val in code_map.items():
            if key in error_msg:
                code = val
                break
        raise HTTPException(status_code=400, detail={"code": code, "message": error_msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}", response_model=ResponseModel)
async def delete_document(
    document_id: str,
    force: bool = Query(False),
):
    try:
        data = knowledge_service.delete_document(document_id, force=force)
        if data is None:
            raise HTTPException(status_code=404, detail="文档不存在")
        return ResponseModel(data={"storageInfo": data.model_dump()})
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"code": 4006, "message": str(e)})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{document_id}/retry", response_model=ResponseModel)
async def retry_document(
    document_id: str,
    fromStep: str = Query("slice"),
):
    try:
        data = knowledge_service.retry_document(document_id, from_step=fromStep)
        if not data:
            raise HTTPException(status_code=404, detail="文档不存在")
        return ResponseModel(data={"document": data.model_dump()})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/chunks", response_model=ResponseModel)
async def get_document_chunks(
    document_id: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
):
    try:
        data = knowledge_service.get_document_chunks(document_id, page=page, pageSize=pageSize)
        if not data:
            raise HTTPException(status_code=404, detail="文档不存在")
        return ResponseModel(data=data.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/content", response_model=ResponseModel)
async def get_document_content(document_id: str):
    try:
        data = knowledge_service.get_document_content(document_id)
        if not data:
            raise HTTPException(status_code=404, detail="文档不存在")
        return ResponseModel(data=data.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/storage", response_model=ResponseModel)
async def get_storage_info():
    try:
        data = knowledge_service.get_storage_info()
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 2. 文档处理状态 ==========
@router.get("/documents/{document_id}/status", response_model=ResponseModel)
async def get_document_status(document_id: str):
    try:
        data = knowledge_service.get_document_status(document_id)
        if not data:
            raise HTTPException(status_code=404, detail="文档不存在")
        return ResponseModel(data=data.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/status/batch", response_model=ResponseModel)
async def batch_get_status(request: BatchStatusRequest):
    try:
        data = knowledge_service.batch_get_status(request.documentIds)
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 3. 知识召回设置 ==========
@router.get("/recall/settings", response_model=ResponseModel)
async def get_recall_settings():
    try:
        data = knowledge_service.get_recall_settings()
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/recall/settings", response_model=ResponseModel)
async def update_recall_settings(params: RecallSettingsUpdate):
    try:
        data = knowledge_service.update_recall_settings(params)
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/reprocess", response_model=ResponseModel)
async def reprocess_documents(request: ReprocessRequest):
    try:
        data = knowledge_service.reprocess_documents(request.chunkSize, request.chunkOverlap)
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 4. 召回测试 ==========
@router.post("/recall/test", response_model=ResponseModel)
async def test_recall(request: RecallTestRequest):
    try:
        data = knowledge_service.test_recall(request)
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail={"code": 5005, "message": str(e)})


@router.get("/recall/test/history", response_model=ResponseModel)
async def get_recall_test_history(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
):
    try:
        data = knowledge_service.get_recall_test_history(page=page, pageSize=pageSize)
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 5. 统计信息 ==========
@router.get("/statistics/documents", response_model=ResponseModel)
async def get_document_statistics():
    try:
        data = knowledge_service.get_document_statistics()
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/processing", response_model=ResponseModel)
async def get_processing_statistics():
    try:
        data = knowledge_service.get_processing_statistics()
        return ResponseModel(data=data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-doc", summary="上传标准化文档至知识库")
async def upload_standardized_doc(
    request: UploadDocToKnowledgeBaseRequest,
):
    try:
        from datetime import datetime
        import uuid as _uuid
        from app.models.knowledge_base import UploadDocToKnowledgeBaseData

        doc_id = f"kb_doc_{_uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat() + "Z"

        knowledge_service.documents[doc_id] = {
            "id": doc_id,
            "name": request.title,
            "format": "md",
            "size": len(request.content.encode("utf-8")),
            "uploadTime": now,
            "status": "success",
            "chunkCount": 0,
            "source_requirement_id": request.requirementId,
            "source_template_id": request.templateId,
            "tags": request.tags or [],
            "content": request.content,
        }

        return ResponseModel(
            message="上传成功",
            data=UploadDocToKnowledgeBaseData(
                docId=doc_id,
                title=request.title,
                status="success",
                uploadedAt=now,
            ).model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
