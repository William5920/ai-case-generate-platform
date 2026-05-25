from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm_client import LLMClient


class QualityService:

    def __init__(self):
        self._llm_client = LLMClient()

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

        result = await self._llm_client.chat_with_schema(
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

        overall = result.get("overall", 0)
        level = result.get("level", "较差")
        completeness = result.get("completeness", {"score": 0, "details": []})
        clarity = result.get("clarity", {"score": 0, "issues": []})
        consistency = result.get("consistency", {"score": 0, "issues": []})
        suggestions = result.get("suggestions", [])

        return {
            "overall": overall,
            "level": level,
            "completeness": completeness,
            "clarity": clarity,
            "consistency": consistency,
            "suggestions": suggestions
        }


quality_service = QualityService()
