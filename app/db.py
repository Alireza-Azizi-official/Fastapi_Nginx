import certifi
from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .models import User, Item
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        tls=True,
        tlsCAFile=certifi.where()
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
