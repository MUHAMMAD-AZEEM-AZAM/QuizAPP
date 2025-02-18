import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from quiz_generate import generate_quiz_from_book
from database import books_collection  # Used if needed elsewhere
from dotenv import load_dotenv
from models import Book
from typing import List
from bson import ObjectId
import logging

load_dotenv()

quiz_router = APIRouter()

# Dummy dependency for current user (replace with your JWT auth dependency)
def get_current_user():
    return {"user_id": "sample_user_id"}

@quiz_router.post("/generate_book_quiz/")
async def generate_book_quiz_endpoint(
    book_file: UploadFile = File(...),
    book_name: str = "Default Book Name",
    current_user: dict = Depends(get_current_user)
):
    if book_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Save file in 'upload' folder
    upload_dir = os.path.join(os.getcwd(), "upload")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_path = os.path.join(upload_dir, book_file.filename)
    try:
        with open(file_path, "wb") as f:
            content = await book_file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {e}")
    
    try:
        book_quiz = await generate_quiz_from_book(file_path, current_user["user_id"], book_name)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error generating book quiz: {e}")
    
    os.remove(file_path)
    return {"message": "Book quiz generated and stored successfully"}



@quiz_router.get("/books/{user_id}")
async def get_books_by_user(user_id: str):
    """
    Retrieves all books for the given user_id and removes the chapter quizzes from the response.
    """
    try:
        logging.info(f"Querying for books with user_id: {user_id}")
        
        # Query for books with matching user_id
        books_cursor = books_collection.find({"user_id": user_id})
        books = []
        async for book in books_cursor:
            logging.info(f"Found book: {book}")
            
            # Convert the _id to a string
            book["_id"] = str(book["_id"])
            
            # Remove the 'quiz' key from each chapter to avoid returning quiz details
            if "chapters" in book:
                for chapter in book["chapters"]:
                    chapter.pop("quiz", None)  # Safely remove 'quiz' if present
            
            books.append(book)
        
        logging.info(f"Total books found: {len(books)}")
        return {"message": "Books found for user", "books": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving books: {e}")