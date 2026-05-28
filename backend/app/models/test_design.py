from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ResponseModel(BaseModel):
    success: bool = True
    code: int = 200
    message: str = "操作成功"
    data: Optional[Any] = None
    traceId: str = Field(default_factory=lambda: f"trace-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")


class RequirementListItem(BaseModel):
    id: str
    title: str
    status: str
    statusText: str
    date: str
    testPointCount: int
    caseCount: int
    source: str = "standardization"


class RequirementListResponse(BaseModel):
    list: List[RequirementListItem]
    total: int
    page: int
    pageSize: int


class SplitRequirementInput(BaseModel):
    content: str
    selected: bool = True


class ImportRequirementRequest(BaseModel):
    title: str
    splitRequirements: List[SplitRequirementInput]
    standardizedContent: Optional[str] = None
    templateId: Optional[str] = None


class ImportRequirementResponse(BaseModel):
    id: str
    title: str
    status: str
    statusText: str
    date: str
    testPointCount: int = 0
    caseCount: int = 0
    source: str = "standardization"


class MindMapNodeData(BaseModel):
    id: str
    text: str
    expand: bool = True
    level: str = Field(..., alias="_level")
    status: Optional[str] = Field(None, alias="_status")
    source: Optional[str] = Field(None, alias="_source")
    marked: Optional[bool] = Field(None, alias="_marked")
    case_property: Optional[str] = Field(None, alias="_caseProperty")
    note: Optional[str] = None
    description: Optional[str] = None
    pre_condition: Optional[str] = Field(None, alias="_preCondition")
    steps: Optional[List] = None

    model_config = {"populate_by_name": True}


class MindMapNode(BaseModel):
    data: MindMapNodeData
    children: List['MindMapNode'] = []


MindMapNode.model_rebuild()


class TestPointCreate(BaseModel):
    requirementNodeId: str
    text: str
    description: Optional[str] = None


class TestPointUpdate(BaseModel):
    text: str


class TestPointMark(BaseModel):
    marked: bool


class TestPointResponse(BaseModel):
    id: str
    text: str
    _source: str = "人工"


class TestCaseStep(BaseModel):
    name: str
    description: str
    stepExpectedResult: str


class TestCaseCreate(BaseModel):
    text: str
    caseProperty: str
    preCondition: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None


class TestCaseUpdate(BaseModel):
    text: str
    caseProperty: str
    preCondition: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None


class TestCaseMark(BaseModel):
    marked: bool


class TestCaseResponse(BaseModel):
    id: str
    text: str
    caseProperty: str
    preCondition: Optional[str] = None
    steps: Optional[List[TestCaseStep]] = None


class BatchDeleteRequest(BaseModel):
    ids: List[str]


class AIAdjustStart(BaseModel):
    requirementId: str
    nodeId: str
    nodeType: str
    markedNodeIds: Optional[List[str]] = None


class AIAdjustApply(BaseModel):
    currentMindMapData: Dict[str, Any]
    markedTestPointTexts: Optional[List[str]] = None
    nodeType: str


class AIAdjustApplyResponse(BaseModel):
    adjustedMindMapData: Dict[str, Any]
    addedCount: int
    removedCount: int
    preservedCount: int


class GenerateRequest(BaseModel):
    useKnowledgeBase: Optional[bool] = False


class GenerateResponse(BaseModel):
    taskId: str


class TaskStatusResponse(BaseModel):
    taskId: str
    requirementId: str = ""
    status: str
    progress: int
    progressText: str


class MessageCreate(BaseModel):
    content: str
