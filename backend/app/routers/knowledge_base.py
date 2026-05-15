from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import uuid
from datetime import datetime
import shutil
import mimetypes
from app.models.knowledge_base import Document, DocumentCreate, KnowledgeRecallParams, RecallTestRequest, RecallTestResponse
from app.core.config import settings
from app.services.knowledge_base import KnowledgeBaseService

router = APIRouter()

# 初始化知识库服务
knowledge_service = KnowledgeBaseService()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/docs", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Query(..., description="文档标题"),
    description: Optional[str] = Query(None, description="文档描述")
):
    """上传文档到知识库"""
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        # 使用mimetypes猜测文件类型，替代magic库
        file_type, _ = mimetypes.guess_type(file_path)
        if file_type is None:
            file_type = file.content_type or "application/octet-stream"
        
        # 创建文档记录
        document = Document(
            id=uuid.uuid4(),
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),  # 临时用户ID
            title=title,
            description=description,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            created_at=datetime.utcnow()
        )
        
        # 文档切片和向量化处理
        knowledge_service.process_document(document)
        
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")

@router.get("/docs", response_model=List[Document])
async def get_documents(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数")
):
    """获取文档列表"""
    return knowledge_service.get_documents(skip=skip, limit=limit)

@router.get("/docs/{document_id}", response_model=Document)
async def get_document(document_id: uuid.UUID):
    """查看文档详情"""
    document = knowledge_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    return document

@router.delete("/docs/{document_id}")
async def delete_document(document_id: uuid.UUID):
    """删除已上传的文档"""
    success = knowledge_service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"message": "文档删除成功"}

@router.get("/docs/{document_id}/content")
async def get_document_content(document_id: uuid.UUID):
    """查看文档内容"""
    document = knowledge_service.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="文档文件不存在")
    
    return FileResponse(
        path=document.file_path,
        filename=os.path.basename(document.file_path),
        media_type=document.file_type
    )

@router.put("/recall-params")
async def update_recall_params(params: KnowledgeRecallParams):
    """调整知识召回相关参数"""
    knowledge_service.update_recall_params(params)
    return {"message": "召回参数更新成功", "params": params}

@router.post("/recall-test", response_model=RecallTestResponse)
async def test_recall(request: RecallTestRequest):
    """进行召回准确率测试"""
    results = knowledge_service.test_recall(request.query, request.params)
    return RecallTestResponse(
        query=request.query,
        results=results,
        total=len(results)
    )
