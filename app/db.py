from contextlib import asynccontextmanager

import certifi
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings
from .models import Item, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(
        settings.MONGODB_URI, tls=True, tlsCAFile=certifi.where()
    )
    try:
        await init_beanie(
            database=client[settings.MONGODB_DB],
            document_models=[User, Item],
        )
        print("Connected to MongoDB Atlas successfully")
        yield
    finally:
        client.close()
        print("MongoDB connection closed")
