from typing import Optional, List
from pydantic import BaseModel, Field


class StandardizeRequest(BaseModel):
    requirementId: str
    templateId: str
    inputMode: str = Field(..., pattern=r"^(text|file)$")
    rawContent: Optional[str] = None
    fileId: Optional[str] = None
    exploreData: Optional[List[dict]] = None


class StandardizeData(BaseModel):
    requirementId: str
    standardizedContent: str
    templateId: str
    versionId: str
    versionNumber: int = 1
    completedAt: str


class StandardizeResultData(BaseModel):
    requirementId: str
    standardizedContent: str
    currentVersionId: str
    currentVersionNumber: int
    updatedAt: str


class SendAdjustMessageRequest(BaseModel):
    requirementId: str
    message: str
    currentContent: str
    templateId: Optional[str] = None
    context: Optional[dict] = None


class ProposalData(BaseModel):
    pendingContent: str
    changeSummary: str


class AdjustChatData(BaseModel):
    messageId: str
    role: str = "assistant"
    content: str
    type: Optional[str] = None
    proposal: Optional[ProposalData] = None
    createdAt: str


class AdjustMessageItem(BaseModel):
    messageId: str
    role: str
    content: str
    type: Optional[str] = None
    proposal: Optional[ProposalData] = None
    confirmed: Optional[bool] = None
    rejected: Optional[bool] = None
    createdAt: str


class AdjustHistoryData(BaseModel):
    messages: List[AdjustMessageItem] = []


class AdoptProposalRequest(BaseModel):
    requirementId: str


class AdoptProposalData(BaseModel):
    requirementId: str
    newContent: str
    newVersionId: str
    newVersionNumber: int
    changeSummary: str


class RejectProposalRequest(BaseModel):
    requirementId: str


class QualityScoreRequest(BaseModel):
    requirementId: str
    content: str
    templateId: Optional[str] = "srs"


class QualityDetailItem(BaseModel):
    section: str
    ok: bool
    suggestion: Optional[str] = None


class CompletenessData(BaseModel):
    score: int
    details: List[QualityDetailItem] = []


class ClarityData(BaseModel):
    score: int
    issues: List[str] = []


class ConsistencyData(BaseModel):
    score: int
    issues: List[str] = []


class QualityScoreData(BaseModel):
    overall: int
    level: str
    completeness: CompletenessData
    clarity: ClarityData
    consistency: ConsistencyData
    suggestions: List[str] = []
