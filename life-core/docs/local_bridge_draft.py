```python
from life_core_client import LifeCoreClient
import asyncio

class LifeBridge:
    _client = None

    @classmethod
    async def _get_client(cls):
        if cls._client is None:
            cls._client = LifeCoreClient(timeout=8)
        return cls._client

    @classmethod
    async def state(cls) -> dict | None:
        try:
            client = await cls._get_client()
            return await client.state()
        except:
            return None

    @classmethod
    async def recall(cls, query: str) -> list[dict]:
        try:
            client = await cls._get_client()
            return await client.recall(query)
        except:
            return []

    @classmethod
    async def event(cls, kind: str, text: str, emo: str = "") -> dict | None:
        try:
            client = await cls._get_client()
            return await client.event(kind, text, emo)
        except:
            return None

    @classmethod
    async def facts(cls, limit: int = 20) -> list[dict]:
        try:
            client = await cls._get_client()
            return await client.facts(limit)
        except:
            return []

    @classmethod
    async def intents(cls) -> list[dict]:
        try:
            client = await cls._get_client()
            return await client.intents()
        except:
            return []

    @classmethod
    async def diary(cls) -> dict | None:
        try:
            client = await cls._get_client()
            return await client.diary()
        except:
            return None

    @classmethod
    async def consolidate(cls) -> dict | None:
        try:
            client = await cls._get_client()
            return await client.consolidate()
        except:
            return None

# 示例调用
async def main():
    state = await LifeBridge.state()
    print(state)

    recall = await LifeBridge.recall("example query")
    print(recall)

    event = await LifeBridge.event("example kind", "example text", "example emo")
    print(event)

    facts = await LifeBridge.facts(10)
    print(facts)

    intents = await LifeBridge.intents()
    print(intents)

    diary = await LifeBridge.diary()
    print(diary)

    consolidate = await LifeBridge.consolidate()
    print(consolidate)

asyncio.run(main())
```