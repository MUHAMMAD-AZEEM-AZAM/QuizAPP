from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv() 
import os

MONGO_URL = os.getenv("MONGO_URL") # Adjust if necessary
DATABASE_NAME = "quiz_db"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]
# Collection to store books (each book document includes chapters and questions)
books_collection = db["books"]
