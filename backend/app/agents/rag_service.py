from typing import List
from dataclasses import dataclass
from app.services.knowledge_base import KnowledgeBaseService
from app.agents.llm_client import LLMClient
from app.core.config import settings


@dataclass
class RecallResult:
    content: str
    score: float
    document_id: str
    chunk_id: int


class RAGService:
    def __init__(self, kb_service: KnowledgeBaseService, llm_client: LLMClient):
        self.kb_service = kb_service
        self.llm_client = llm_client

    async def recall(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
    ) -> List[RecallResult]:
        try:
            raw_results = self.kb_service.test_recall(query, params=None)
            results = []
            for r in raw_results:
                score = r.get("score", 0)
                if score >= threshold:
                    results.append(RecallResult(
                        content=r.get("content", ""),
                        score=score,
                        document_id=r.get("document_id", ""),
                        chunk_id=r.get("chunk_id", 0),
                    ))
            return results[:top_k]
        except Exception:
            return []

    async def recall_and_rerank(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.7,
        final_k: int = 3,
    ) -> List[RecallResult]:
        results = await self.recall(query, top_k=top_k, threshold=threshold)
        if not results:
            return []

        if len(results) <= final_k:
            return results

        reranked = await self._rerank_with_llm(query, results)
        return reranked[:final_k]

    async def _rerank_with_llm(self, query: str, results: List[RecallResult]) -> List[RecallResult]:
        numbered = []
        for i, r in enumerate(results, 1):
            numbered.append(f"{i}. {r.content[:300]}")

        prompt = (
            "你是一个知识检索专家。请根据查询问题，对以下检索结果按相关性从高到低重新排序。\n"
            "只返回排序后的编号列表，用逗号分隔。\n\n"
            f"查询问题：{query}\n\n"
            f"检索结果：\n" + "\n".join(numbered) + "\n\n排序结果："
        )

        try:
            content = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                model=settings.OPENAI_MODEL_ANALYZE,
                temperature=0.1,
                max_tokens=100,
            )
            indices = [int(x.strip()) for x in content.strip().split(",") if x.strip().isdigit()]
            reranked = []
            for idx in indices:
                if 1 <= idx <= len(results):
                    reranked.append(results[idx - 1])
            for r in results:
                if r not in reranked:
                    reranked.append(r)
            return reranked
        except Exception:
            return results
