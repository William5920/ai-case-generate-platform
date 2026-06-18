from typing import Optional, List
from pydantic import BaseModel, Field


class StartExploreRequest(BaseModel):
    requirementId: Optional[str] = None
    templateId: Optional[str] = "user-story"
    rawContent: Optional[str] = None
    fileId: Optional[str] = None
    inputMode: Optional[str] = "text"
    title: Optional[str] = None


class SendExploreMessageRequest(BaseModel):
    sessionId: Optional[str] = None
    requirementId: Optional[str] = None
    message: str = ""
    dimensionKey: Optional[str] = None


class ExploreFirstQuestion(BaseModel):
    dimensionKey: str
    dimensionLabel: str
    content: str


class StartExploreData(BaseModel):
    sessionId: str
    requirementId: str
    templateId: str
    totalDimensions: int
    exploredDimensions: List[str] = []
    understandingScore: int = 0
    firstQuestion: Optional[ExploreFirstQuestion] = None
    status: str = "active"


class ExploreMessageItem(BaseModel):
    messageId: str
    role: str
    content: str
    type: Optional[str] = None
    dimensionKey: Optional[str] = None
    dimensionLabel: Optional[str] = None
    quickReplies: Optional[List[str]] = None
    replied: Optional[bool] = None
    createdAt: str


class ExploreChatData(BaseModel):
    messageId: str
    role: str = "assistant"
    content: str
    type: Optional[str] = None
    dimensionKey: Optional[str] = None
    dimensionLabel: Optional[str] = None
    quickReplies: Optional[List[str]] = None
    exploredDimensions: List[str] = []
    totalDimensions: int = 0
    understandingScore: int = 0
    canGenerate: bool = False
    createdAt: str


class ExploreHistoryData(BaseModel):
    sessionId: str
    messages: List[ExploreMessageItem] = []
    exploredDimensions: List[str] = []
    totalDimensions: int = 0
    understandingScore: int = 0


class ExploreDataItem(BaseModel):
    dimensionKey: str
    dimensionLabel: str
    content: str


class ExploreStatusData(BaseModel):
    sessionId: str
    requirementId: str
    templateId: str
    status: str
    totalDimensions: int
    exploredDimensions: List[str] = []
    understandingScore: int = 0
    canGenerate: bool = False
    exploreData: List[ExploreDataItem] = []
    startedAt: Optional[str] = None
    updatedAt: Optional[str] = None
