import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="sk-641bf49205cf4f9f99ccdc4de9734385",
    base_url="https://api.deepseek.com",
)

async def test():
    r = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "返回json：{'a':1}"}
        ],
        response_format={"type": "json_object"},
    )

    print(r.choices[0].message.content)

asyncio.run(test())