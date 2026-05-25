import json
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.agents.llm_client import LLMClient
from app.agents.prompts import PromptTemplates
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


TEMPLATES_DATA = [
    {
        "id": "srs",
        "name": "SRS 需求规格说明书",
        "description": "适用于瀑布式开发，基于 IEEE 830 标准，文档完整详细",
        "icon": "📋",
        "tags": ["瀑布式", "详细", "完整"],
        "dimensions": [
            {"key": "purpose", "label": "编写目的", "question": "这份需求文档的编写目的是什么？主要面向哪些读者？"},
            {"key": "background", "label": "项目背景", "question": "请描述项目的业务背景和要解决的问题？"},
            {"key": "terms", "label": "术语定义", "question": "项目中是否有需要统一定义的专业术语或缩写？"},
            {"key": "goal", "label": "业务目标", "question": "本需求要达成的核心业务目标是什么？"},
            {"key": "role", "label": "用户角色", "question": "系统涉及哪些用户角色？各角色的职责是什么？"},
            {"key": "flow", "label": "核心业务流程", "question": "请描述核心业务流程的主要步骤？"},
            {"key": "functional", "label": "功能需求", "question": "系统需要实现哪些具体功能？请逐一描述。"},
            {"key": "performance", "label": "性能需求", "question": "对系统性能有什么要求？如响应时间、并发量、吞吐量等。"},
            {"key": "security", "label": "安全性需求", "question": "对数据安全、访问控制、审计日志等有什么要求？"},
            {"key": "availability", "label": "可用性需求", "question": "对系统可用率、故障恢复时间等有什么要求？"},
            {"key": "compatibility", "label": "兼容性需求", "question": "需要兼容哪些浏览器、操作系统或设备？"},
            {"key": "tech_constraint", "label": "技术约束", "question": "是否有技术栈、框架、部署环境等技术限制？"},
            {"key": "business_constraint", "label": "业务约束", "question": "是否有合规要求、行业标准等业务限制？"},
            {"key": "regulatory", "label": "法规约束", "question": "是否需要遵守数据保护法、行业监管等法规？"},
            {"key": "exception", "label": "异常场景", "question": "需要处理哪些异常场景？如网络超时、数据校验失败等。"}
        ],
        "sections": [
            {
                "id": "intro", "title": "1. 引言", "required": True,
                "children": [
                    {"id": "intro-purpose", "title": "1.1 编写目的", "placeholder": "说明本文档的编写目的和预期读者"},
                    {"id": "intro-background", "title": "1.2 项目背景", "placeholder": "描述项目背景、业务场景和要解决的问题"},
                    {"id": "intro-terms", "title": "1.3 术语定义", "placeholder": "定义文档中使用的专业术语和缩写"}
                ]
            },
            {
                "id": "overview", "title": "2. 需求概述", "required": True,
                "children": [
                    {"id": "overview-goal", "title": "2.1 业务目标", "placeholder": "描述本需求要达成的业务目标"},
                    {"id": "overview-role", "title": "2.2 用户角色", "placeholder": "列出涉及的用户角色及其职责"},
                    {"id": "overview-flow", "title": "2.3 核心业务流程", "placeholder": "描述核心业务流程的主要步骤"}
                ]
            },
            {
                "id": "functional", "title": "3. 功能需求", "required": True,
                "children": [
                    {"id": "func-module-1", "title": "3.1 功能模块一", "placeholder": "描述第一个功能模块的详细需求"},
                    {"id": "func-module-2", "title": "3.2 功能模块二", "placeholder": "描述第二个功能模块的详细需求"}
                ]
            },
            {
                "id": "non-functional", "title": "4. 非功能需求", "required": True,
                "children": [
                    {"id": "nf-performance", "title": "4.1 性能需求", "placeholder": "如响应时间、并发量、吞吐量等指标"},
                    {"id": "nf-security", "title": "4.2 安全性需求", "placeholder": "如数据加密、访问控制、审计日志等"},
                    {"id": "nf-availability", "title": "4.3 可用性需求", "placeholder": "如系统可用率、故障恢复时间等"},
                    {"id": "nf-compatibility", "title": "4.4 兼容性需求", "placeholder": "如浏览器兼容、操作系统兼容等"}
                ]
            },
            {
                "id": "constraints", "title": "5. 约束条件", "required": True,
                "children": [
                    {"id": "const-tech", "title": "5.1 技术约束", "placeholder": "如开发语言、框架、部署环境等技术限制"},
                    {"id": "const-business", "title": "5.2 业务约束", "placeholder": "如合规要求、行业标准等业务限制"},
                    {"id": "const-regulatory", "title": "5.3 法规约束", "placeholder": "如数据保护法、行业监管要求等法规限制"}
                ]
            },
            {
                "id": "exceptions", "title": "6. 异常场景处理", "required": True,
                "children": [
                    {"id": "exc-1", "title": "6.1 异常场景一", "placeholder": "描述异常场景及处理方式"},
                    {"id": "exc-2", "title": "6.2 异常场景二", "placeholder": "描述异常场景及处理方式"}
                ]
            }
        ]
    },
    {
        "id": "user-story",
        "name": "用户故事需求文档",
        "description": "适用于敏捷式开发，以用户故事为核心，文档简洁聚焦",
        "icon": "📝",
        "tags": ["敏捷式", "简洁", "聚焦"],
        "dimensions": [
            {"key": "background", "label": "背景与目标", "question": "请描述项目的背景和要达成的目标？"},
            {"key": "scope", "label": "范围与优先级", "question": "本次需求的范围是什么？哪些功能优先级最高？"},
            {"key": "role", "label": "用户角色", "question": "系统涉及哪些用户角色？请描述各角色的特征。"},
            {"key": "story", "label": "用户故事", "question": "请描述核心的用户故事：作为XX，我希望XX，以便XX。"},
            {"key": "acceptance", "label": "验收标准", "question": "每个用户故事的验收标准是什么？怎样算完成？"},
            {"key": "rule", "label": "业务规则", "question": "有哪些业务规则需要遵守？如计算逻辑、状态流转等。"},
            {"key": "data", "label": "数据需求", "question": "涉及哪些核心数据实体？数据之间的关系是什么？"},
            {"key": "non-functional", "label": "非功能需求", "question": "对性能、安全性、可用性等有什么关键要求？"},
            {"key": "dependency", "label": "依赖与假设", "question": "有哪些外部依赖？做了哪些假设条件？"}
        ],
        "sections": [
            {
                "id": "overview", "title": "1. 需求概述", "required": True,
                "children": [
                    {"id": "ov-background", "title": "1.1 背景与目标", "placeholder": "描述项目背景和要达成的目标"},
                    {"id": "ov-scope", "title": "1.2 范围与优先级", "placeholder": "明确需求范围和优先级排序"}
                ]
            },
            {
                "id": "roles", "title": "2. 用户角色", "required": True,
                "children": [
                    {"id": "role-1", "title": "2.1 角色一", "placeholder": "描述用户角色的特征和职责"},
                    {"id": "role-2", "title": "2.2 角色二", "placeholder": "描述用户角色的特征和职责"}
                ]
            },
            {
                "id": "stories", "title": "3. 用户故事", "required": True,
                "children": [
                    {"id": "story-1", "title": "3.1 用户故事一", "placeholder": "作为XX，我希望XX，以便XX"},
                    {"id": "story-1-acceptance", "title": "3.1.1 验收标准", "placeholder": "列出验收标准，怎样算完成"},
                    {"id": "story-2", "title": "3.2 用户故事二", "placeholder": "作为XX，我希望XX，以便XX"},
                    {"id": "story-2-acceptance", "title": "3.2.2 验收标准", "placeholder": "列出验收标准，怎样算完成"}
                ]
            },
            {
                "id": "rules", "title": "4. 业务规则", "required": True,
                "children": [
                    {"id": "rule-1", "title": "4.1 业务规则一", "placeholder": "描述业务规则，如计算逻辑、状态流转等"},
                    {"id": "rule-2", "title": "4.2 业务规则二", "placeholder": "描述业务规则"}
                ]
            },
            {
                "id": "data", "title": "5. 数据需求", "required": True,
                "children": [
                    {"id": "data-entity", "title": "5.1 核心数据实体", "placeholder": "列出核心数据实体及其属性"},
                    {"id": "data-relation", "title": "5.2 数据关系", "placeholder": "描述数据实体之间的关系"}
                ]
            },
            {
                "id": "non-functional", "title": "6. 非功能需求", "required": False,
                "children": [
                    {"id": "nf-key", "title": "6.1 关键非功能需求", "placeholder": "列出关键的性能、安全、可用性要求"}
                ]
            },
            {
                "id": "dependencies", "title": "7. 依赖与假设", "required": False,
                "children": [
                    {"id": "dep-external", "title": "7.1 外部依赖", "placeholder": "列出外部系统或服务依赖"},
                    {"id": "dep-assumption", "title": "7.2 假设条件", "placeholder": "列出已做的假设条件"}
                ]
            }
        ]
    }
]


class TemplateService:

    def __init__(self):
        self._templates = {t["id"]: t for t in TEMPLATES_DATA}
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)

    def get_template_list(self) -> dict:
        templates = []
        for t in TEMPLATES_DATA:
            templates.append({
                "id": t["id"],
                "name": t["name"],
                "description": t["description"],
                "icon": t["icon"],
                "tags": t["tags"],
                "dimensions": t["dimensions"],
                "sections": t["sections"]
            })
        return {"templates": templates}

    def get_template_detail(self, template_id: str) -> Optional[dict]:
        template = self._templates.get(template_id)
        if not template:
            return None
        return {
            "id": template["id"],
            "name": template["name"],
            "description": template["description"],
            "icon": template["icon"],
            "tags": template["tags"],
            "dimensions": template["dimensions"],
            "sections": template["sections"]
        }

    def get_template_dimensions(self, template_id: str) -> List[dict]:
        template = self._templates.get(template_id)
        if not template:
            return []
        return template["dimensions"]

    def get_template_sections_text(self, template_id: str) -> str:
        template = self._templates.get(template_id)
        if not template:
            return ""
        lines = []
        for section in template["sections"]:
            lines.append(f"- {section['title']}")
            for child in section.get("children", []):
                lines.append(f"  - {child['title']}")
        return "\n".join(lines)

    async def recommend_template(self, content: str, input_mode: str = "text") -> dict:
        if not self._llm_available:
            return {
                "recommendedTemplateId": "srs",
                "confidence": 0.5,
                "reason": "AI服务暂不可用，默认推荐SRS模板"
            }

        prompt = PromptTemplates.TEMPLATE_RECOMMEND.format(content=content)
        schema = PromptTemplates.TEMPLATE_RECOMMEND_SCHEMA

        messages = [{"role": "user", "content": prompt}]
        try:
            result = await self._llm_client.chat_with_schema(messages, schema)
        except Exception as e:
            logger.warning(f"LLM call failed for template recommendation: {e}")
            return {
                "recommendedTemplateId": "srs",
                "confidence": 0.5,
                "reason": "AI服务调用失败，默认推荐SRS模板"
            }

        recommended_id = result.get("recommended_template_id", "srs")
        if recommended_id not in self._templates:
            recommended_id = "srs"

        return {
            "recommendedTemplateId": recommended_id,
            "confidence": result.get("confidence", 0.5),
            "reason": result.get("reason", "")
        }


template_service = TemplateService()
