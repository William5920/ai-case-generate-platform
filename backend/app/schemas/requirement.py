from typing import Optional, List
from pydantic import BaseModel, Field


class CreateRequirementRequest(BaseModel):
    title: str = Field(..., max_length=200)
    inputMode: str = Field(..., pattern=r"^(text|file)$")
    rawContent: Optional[str] = None
    fileId: Optional[str] = None
    templateId: Optional[str] = "user-story"


class UpdateRequirementRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    rawContent: Optional[str] = None
    templateId: Optional[str] = None
    standardizedContent: Optional[str] = None
    exploreData: Optional[list] = None
    status: Optional[str] = None


class RequirementListQuery(BaseModel):
    pageNo: int = Field(1, ge=1)
    pageSize: int = Field(20, ge=1, le=100)
    keyword: Optional[str] = None
    status: Optional[str] = None


class ExploreDataItem(BaseModel):
    dimensionKey: str
    dimensionLabel: str
    content: str


class SplitRequirementItem(BaseModel):
    id: str
    content: str
    order: int


class FileInfoSchema(BaseModel):
    fileName: str
    fileSize: int
    fileType: str

    class Config:
        from_attributes = True


class RequirementDetail(BaseModel):
    id: str
    title: str
    inputMode: str
    rawContent: Optional[str] = None
    templateId: Optional[str] = None
    fileInfo: Optional[FileInfoSchema] = None
    exploreData: Optional[list] = None
    standardizedContent: Optional[str] = None
    splitRequirements: Optional[List[SplitRequirementItem]] = None
    status: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class RequirementListItem(BaseModel):
    id: str
    title: str
    status: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class RequirementListData(BaseModel):
    items: List[RequirementListItem]
    pageNo: int
    pageSize: int
    total: int
