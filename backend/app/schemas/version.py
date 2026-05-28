from typing import Optional, List
from pydantic import BaseModel


class VersionItem(BaseModel):
    versionId: str
    versionNumber: int
    description: Optional[str] = None
    createdAt: str


class VersionListData(BaseModel):
    versions: List[VersionItem] = []
    currentVersionId: str


class VersionDetailData(BaseModel):
    versionId: str
    versionNumber: int
    content: str
    description: Optional[str] = None
    createdAt: str


class RestoreVersionData(BaseModel):
    newVersionId: str
    newVersionNumber: int
    content: str
    description: str


class DiffLineItem(BaseModel):
    lineNumber: int
    text: str
    type: str


class DiffSummary(BaseModel):
    addedCount: int = 0
    modifiedCount: int = 0
    removedCount: int = 0


class VersionDiffData(BaseModel):
    fromVersionId: str
    toVersionId: str
    diffLines: List[DiffLineItem] = []
    summary: DiffSummary
