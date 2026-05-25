import json
import asyncio
from typing import List, Dict, Optional
import httpx
from app.core.config import settings


class LLMClient:
    def __init__(self):
        self.http_client = httpx.AsyncClient(
            base_url=settings.OPENAI_BASE_URL,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
            timeout=120.0
        )
        self.max_retries = settings.OPENAI_MAX_RETRIES

    async def chat(
        self,
        messages: List[Dict],
        model: str = None,
        temperature: float = 0.7,
        response_format: Optional[Dict] = None,
        max_tokens: int = 4096,
    ) -> str:
        model = model or settings.OPENAI_MODEL
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        for attempt in range(self.max_retries):
            try:
                response = await self.http_client.post("/chat/completions", json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
                    continue
                raise
            except (httpx.RequestError, KeyError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait = 2 ** attempt
                await asyncio.sleep(wait)
        raise RuntimeError("LLM调用失败：超过最大重试次数")

    async def chat_with_schema(
        self,
        messages: List[Dict],
        schema_description: str,
        model: str = None,
        temperature: float = 0.5,
        max_tokens: int = 4096,
    ) -> Dict:
        system_msg = messages[0] if messages and messages[0].get("role") == "system" else {"role": "system", "content": ""}
        if messages and messages[0].get("role") == "system":
            remaining = messages[1:]
        else:
            remaining = messages

        enhanced_system = {
            "role": "system",
            "content": system_msg["content"] + "\n\n你必须以JSON格式输出，遵循以下结构：\n" + schema_description
        }
        all_messages = [enhanced_system] + remaining

        content = await self.chat(
            messages=all_messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
        )

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"LLM输出无法解析为JSON: {content[:200]}")

    async def close(self):
        await self.http_client.aclose()
