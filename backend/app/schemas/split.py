from typing import Optional, List
from pydantic import BaseModel


class ExecuteSplitRequest(BaseModel):
    requirementId: Optional[str] = None
    standardizedContent: Optional[str] = None


class SplitItem(BaseModel):
    id: str
    content: str
    order: int


class ExecuteSplitData(BaseModel):
    requirementId: str
    splits: List[SplitItem] = []
    totalCount: int = 0


class SplitListData(BaseModel):
    splits: List[SplitItem] = []
    totalCount: int = 0


class UpdateSplitRequest(BaseModel):
    content: str
    order: Optional[int] = None


class UpdateSplitData(BaseModel):
    id: str
    content: str
    order: int
    updatedAt: str


class AddSplitRequest(BaseModel):
    content: str
    order: Optional[int] = None


class AddSplitData(BaseModel):
    id: str
    content: str
    order: int
    createdAt: str


class ConfirmAndTestRequest(BaseModel):
    requirementId: Optional[str] = None
    title: Optional[str] = None
    splitRequirements: Optional[List[dict]] = None
    standardizedContent: Optional[str] = None
    templateId: Optional[str] = None


class MindMapNodeData(BaseModel):
    text: str
    note: str = ""
    expand: bool = True
    _level: str
    _status: str = "pending"


class MindMapChild(BaseModel):
    data: MindMapNodeData
    children: List = []


class ConfirmAndTestData(BaseModel):
    id: str
    title: str
    status: str = "pending"
    statusText: str = "待生成"
    date: str = ""
    testPointCount: int = 0
    caseCount: int = 0
    source: str = "standardization"
    mindMapData: Optional[dict] = None
