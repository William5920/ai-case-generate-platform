from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.agents.llm_client import LLMClient
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class QualityService:

    def __init__(self):
        self._llm_client = LLMClient()
        self._llm_available = bool(settings.OPENAI_API_KEY)

    async def _call_llm_with_schema(self, messages, schema_description, temperature=0.3, max_tokens=4096):
        if not self._llm_available:
            return None
        try:
            return await self._llm_client.chat_with_schema(messages=messages, schema_description=schema_description, temperature=temperature, max_tokens=max_tokens)
        except Exception as e:
            logger.warning(f"LLM call with schema failed: {e}")
            return None

    async def calculate_quality_score(
        self,
        db: Optional[AsyncSession],
        requirement_id: str,
        content: str,
        template_id: str = "srs"
    ) -> dict:
        prompt = f"""你是一个需求文档质量评审专家。请评估以下需求文档的质量，从完整性、清晰性、一致性三个维度打分。

文档内容：
{content}

模板类型：{"SRS需求规格说明书" if template_id == "srs" else "用户故事需求文档"}

请以JSON格式输出：
{{
  "overall": 0到100的总体评分,
  "level": "优秀(90-100)|良好(70-89)|一般(50-69)|较差(0-49)",
  "completeness": {{
    "score": 0到100的完整性评分,
    "details": [
      {{
        "section": "章节名称",
        "ok": true或false,
        "suggestion": "改进建议（如果ok为false）"
      }}
    ]
  }},
  "clarity": {{
    "score": 0到100的清晰性评分,
    "issues": ["问题1", "问题2"]
  }},
  "consistency": {{
    "score": 0到100的一致性评分,
    "issues": ["问题1", "问题2"]
  }},
  "suggestions": ["总体改进建议1", "总体改进建议2"]
}}"""

        result = await self._call_llm_with_schema(
            messages=[{"role": "user", "content": prompt}],
            schema_description="""{
  "overall": 85,
  "level": "良好",
  "completeness": {
    "score": 80,
    "details": [{"section": "章节", "ok": true, "suggestion": null}]
  },
  "clarity": {"score": 90, "issues": []},
  "consistency": {"score": 85, "issues": []},
  "suggestions": ["建议1"]
}""",
            temperature=0.3
        )

        if result:
            overall = result.get("overall", 0)
            level = result.get("level", "较差")
            completeness = result.get("completeness", {"score": 0, "details": []})
            clarity = result.get("clarity", {"score": 0, "issues": []})
            consistency = result.get("consistency", {"score": 0, "issues": []})
            suggestions = result.get("suggestions", [])
        else:
            overall, level, completeness, clarity, consistency, suggestions = self._fallback_score(content)

        return {
            "overall": overall,
            "level": level,
            "completeness": completeness,
            "clarity": clarity,
            "consistency": consistency,
            "suggestions": suggestions
        }

    def _fallback_score(self, content: str) -> tuple:
        has_headers = any(line.startswith("#") for line in content.split("\n"))
        has_sections = content.count("##") >= 2
        length = len(content)

        completeness_score = 40
        if has_headers:
            completeness_score += 10
        if has_sections:
            completeness_score += 15
        if length > 200:
            completeness_score += 10
        if length > 500:
            completeness_score += 10

        clarity_score = 50
        if length > 100:
            clarity_score += 10
        if has_sections:
            clarity_score += 15

        consistency_score = 60
        overall = int((completeness_score + clarity_score + consistency_score) / 3)

        if overall >= 90:
            level = "优秀"
        elif overall >= 70:
            level = "良好"
        elif overall >= 50:
            level = "一般"
        else:
            level = "较差"

        completeness = {
            "score": completeness_score,
            "details": [{"section": "文档结构", "ok": has_sections, "suggestion": None if has_sections else "建议添加更多章节结构"}]
        }
        clarity = {"score": clarity_score, "issues": [] if clarity_score >= 70 else ["建议补充更多细节描述"]}
        consistency = {"score": consistency_score, "issues": []}
        suggestions = ["AI评分服务暂不可用，以上为基于文档结构的初步评估"] if not self._llm_available else []

        return overall, level, completeness, clarity, consistency, suggestions


quality_service = QualityService()
