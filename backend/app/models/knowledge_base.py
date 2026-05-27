from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ResponseModel(BaseModel):
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None
    traceId: str = Field(default_factory=lambda: f"trace-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")


class DocumentItem(BaseModel):
    id: str
    name: str
    format: str
    size: int
    uploadTime: str
    status: str
    chunkCount: int = 0
    avgChunkLength: int = 0
    errorMessage: Optional[str] = None
    retryCount: int = 0


class DocumentListData(BaseModel):
    total: int
    page: int
    pageSize: int
    documents: List[DocumentItem]


class DocumentMetadata(BaseModel):
    author: Optional[str] = None
    createdAt: Optional[str] = None
    modifiedAt: Optional[str] = None


class DocumentDetailData(BaseModel):
    id: str
    name: str
    format: str
    size: int
    uploadTime: str
    status: str
    chunkCount: int = 0
    avgChunkLength: int = 0
    errorMessage: Optional[str] = None
    retryCount: int = 0
    contentPreview: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None


class StorageInfo(BaseModel):
    usedBytes: int
    maxBytes: int = 2147483648
    usedPercentage: float
    usedText: str


class UploadResponseData(BaseModel):
    document: DocumentItem
    storageInfo: StorageInfo


class DocumentRetryData(BaseModel):
    id: str
    status: str
    retryCount: int


class ChunkMetadata(BaseModel):
    page: Optional[int] = None
    section: Optional[str] = None


class ChunkItem(BaseModel):
    index: int
    content: str
    length: int
    vectorId: Optional[str] = None
    metadata: Optional[ChunkMetadata] = None


class ChunkListData(BaseModel):
    totalChunks: int
    avgChunkLength: int
    chunks: List[ChunkItem]


class DocumentContentData(BaseModel):
    content: str
    length: int
    encoding: str = "utf-8"


class StorageDetailData(StorageInfo):
    documentCount: int = 0
    availableSpace: int = 0
    warningLevel: str = "normal"


class DocumentStatusData(BaseModel):
    status: str
    progress: float = 0
    currentStep: Optional[str] = None
    estimatedTime: Optional[int] = None
    errorMessage: Optional[str] = None
    retryCount: int = 0


class BatchStatusItem(BaseModel):
    documentId: str
    status: str
    progress: float = 0
    currentStep: Optional[str] = None
    errorMessage: Optional[str] = None


class BatchStatusData(BaseModel):
    statuses: List[BatchStatusItem]


class BatchStatusRequest(BaseModel):
    documentIds: List[str]


class RecallSettingsData(BaseModel):
    enabled: bool = True
    topK: int = Field(default=5, ge=1, le=20)
    scoreThreshold: float = Field(default=0.7, ge=0.0, le=1.0)
    chunkSize: int = Field(default=500, ge=100, le=2000)
    chunkOverlap: int = Field(default=50, ge=0, le=500)
    recallStrategy: str = "hybrid"
    updatedAt: Optional[str] = None
    updatedBy: Optional[str] = None


class RecallSettingsUpdate(BaseModel):
    enabled: Optional[bool] = None
    topK: Optional[int] = Field(default=None, ge=1, le=20)
    scoreThreshold: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    chunkSize: Optional[int] = Field(default=None, ge=100, le=2000)
    chunkOverlap: Optional[int] = Field(default=None, ge=0, le=500)
    recallStrategy: Optional[str] = None


class RecallSettingsUpdateData(BaseModel):
    settings: RecallSettingsData
    requiresReprocess: bool = False
    reprocessDocuments: int = 0


class ReprocessRequest(BaseModel):
    chunkSize: int = Field(ge=100, le=2000)
    chunkOverlap: int = Field(ge=0, le=500)


class ReprocessData(BaseModel):
    totalDocuments: int
    processingDocuments: List[str]
    estimatedTime: int


class RecallTestRequest(BaseModel):
    query: str
    topK: Optional[int] = None
    scoreThreshold: Optional[float] = None
    recallStrategy: Optional[str] = None


class RecallTestResultItem(BaseModel):
    index: int
    score: float
    documentId: str
    documentName: str
    chunkIndex: int
    content: str
    length: int
    metadata: Optional[ChunkMetadata] = None


class UsedSettings(BaseModel):
    topK: int
    scoreThreshold: float
    recallStrategy: str


class RecallTestData(BaseModel):
    query: str
    results: List[RecallTestResultItem]
    totalResults: int
    elapsedTime: float
    usedSettings: UsedSettings


class RecallTestHistoryItem(BaseModel):
    id: str
    query: str
    resultCount: int
    elapsedTime: float
    createdAt: str
    settings: UsedSettings


class RecallTestHistoryData(BaseModel):
    total: int
    page: int
    pageSize: int
    history: List[RecallTestHistoryItem]


class DocumentStatisticsData(BaseModel):
    totalDocuments: int = 0
    readyDocuments: int = 0
    processingDocuments: int = 0
    failedDocuments: int = 0
    totalChunks: int = 0
    avgChunksPerDocument: float = 0
    avgChunkLength: float = 0
    byFormat: Dict[str, int] = {}


class ProcessingStatisticsData(BaseModel):
    uploading: int = 0
    slicing: int = 0
    vectorizing: int = 0
    ready: int = 0
    failed: int = 0
    activeProcesses: int = 0
    queueLength: int = 0
    estimatedCompletionTime: int = 0


class UploadDocToKnowledgeBaseRequest(BaseModel):
    requirementId: str
    title: str
    content: str
    templateId: Optional[str] = None
    tags: Optional[List[str]] = None


class UploadDocToKnowledgeBaseData(BaseModel):
    docId: str
    title: str
    status: str = "success"
    uploadedAt: str
