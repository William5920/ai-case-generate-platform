from typing import Optional, List
from pydantic import BaseModel


class DimensionItem(BaseModel):
    key: str
    label: str
    question: str


class SectionChild(BaseModel):
    id: str
    title: str
    placeholder: str


class SectionItem(BaseModel):
    id: str
    title: str
    required: bool
    children: List[SectionChild]


class TemplateItem(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    tags: List[str]
    dimensions: List[DimensionItem]
    sections: List[SectionItem]


class TemplateListData(BaseModel):
    templates: List[TemplateItem]


class RecommendTemplateRequest(BaseModel):
    content: str
    inputMode: str = "text"


class RecommendTemplateData(BaseModel):
    recommendedTemplateId: str
    confidence: float
    reason: str
