from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import User, Item
from .config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    try:
        await init_beanie(database=client[settings.MONGODB_DB], document_models=[User, Item])
        yield
    finally:
        client.close()