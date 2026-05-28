import os

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models.item import Calendar, DeepResearchResult, Event, Goal, Task, TimeSlot

_client: AsyncIOMotorClient | None = None


async def init_db(
    uri: str | None = None,
    db_name: str = "guidance",
) -> None:
    global _client
    uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    _client = AsyncIOMotorClient(uri)
    await init_beanie(
        database=_client[db_name],
        document_models=[Task, Event, Goal, TimeSlot, Calendar, DeepResearchResult],
    )


def close_db() -> None:
    if _client is not None:
        _client.close()
