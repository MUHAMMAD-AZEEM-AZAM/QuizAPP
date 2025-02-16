from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "quiz_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# Collection for individual chapter quizzes
chapters_collection = db["chapters"]

# Collection for the complete book object
books_collection = db["books"]



users_collection = db["users"]
