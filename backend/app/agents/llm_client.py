import json
import asyncio
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI, APIConnectionError, APITimeoutError, RateLimitError, APIStatusError
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class LLMClient:
    def __init__(self):
        self._client = None
        self._cached_base_url = None
        self._cached_api_key = None

    def _get_client(self) -> AsyncOpenAI:
        if (
            self._client is None
            or self._cached_base_url != settings.OPENAI_BASE_URL
            or self._cached_api_key != settings.OPENAI_API_KEY
        ):

            self._cached_base_url = settings.OPENAI_BASE_URL
            self._cached_api_key = settings.OPENAI_API_KEY


            self._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                timeout=30.0,
                max_retries=1,
            )

        return self._client

    async def chat(
        self,
        messages: List[Dict],
        model: str = None,
        temperature: float = 0.7,
        response_format: Optional[Dict] = None,
        max_tokens: int = 4096,
    ) -> str:
        model = model or settings.OPENAI_MODEL
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = await self._get_client().chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.warning(f"LLM rate limited, retrying: {e}")
            await asyncio.sleep(2)
            response = await self._get_client().chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except APITimeoutError as e:
            logger.warning(f"LLM request timed out, retrying: {e}")
            await asyncio.sleep(3)
            response = await self._get_client().chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except APIStatusError as e:
            logger.error(f"LLM API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.warning(f"LLM connection error, recreating client: {e}")
            await self.close()
            await asyncio.sleep(1)
            response = await self._get_client().chat.completions.create(**kwargs)
            return response.choices[0].message.content

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
        if self._client is not None:
            await self._client.close()
            self._client = None
            self._cached_base_url = None
            self._cached_api_key = None
