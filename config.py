from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
# orm
from mongoengine import connect, Document, StringField

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    MONGODB_URI: str = os.getenv("MONGO_DB_URI")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")

settings = Settings()

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]

# Connect to MongoDB orm
def init_orm_db():
    connect(
        db=settings.DATABASE_NAME,
        host=settings.MONGODB_URI
    )
