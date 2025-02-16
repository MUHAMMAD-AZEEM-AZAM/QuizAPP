import os
import tempfile
import json
import re
from fastapi import APIRouter, HTTPException
from models import Quiz  # This now works because Quiz is defined in models.py
from database import books_collection  # Example: if you're storing quiz data in MongoDB
from fastapi import APIRouter, UploadFile, File, HTTPException
from quiz_generate import generate_quiz_from_book

quiz_router = APIRouter()

@quiz_router.post("/quizzes/", response_model=dict)
async def create_quiz(quiz: Quiz):
    quiz_dict = quiz.model_dump()
    # For example, if storing in a MongoDB collection:
    result = await books_collection.insert_one(quiz_dict)
    if result.inserted_id:
        return {"message": "Quiz saved successfully", "quiz_id": str(result.inserted_id)}
    raise HTTPException(status_code=500, detail="Failed to save quiz")

@quiz_router.get("/quizzes/", response_model=dict)
async def get_quizzes():
    quizzes_cursor = books_collection.find()
    quizzes = []
    async for quiz in quizzes_cursor:
        quiz["_id"] = str(quiz["_id"])
        quizzes.append(quiz)
    return {"quizzes": quizzes}


@quiz_router.post("/generate_quiz_from_book/")
async def generate_quiz_from_book_endpoint(book_file: UploadFile = File(...)):
    """
    Accepts a PDF file upload, saves it to the server's "upload" folder,
    calls generate_quiz_from_book to generate a quiz, and returns the quiz JSON.
    """
    if book_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Define the upload folder relative to the current working directory
    upload_dir = os.path.join(os.getcwd(), "upload")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Save the uploaded file to the upload folder
    try:
        file_path = os.path.join(upload_dir, book_file.filename)
        with open(file_path, "wb") as f:
            file_content = await book_file.read()
            f.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving uploaded file: {e}")

    # Generate the quiz by calling our quiz generation function
    try:
        quiz_result = generate_quiz_from_book(file_path)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {e}")
    
    # Comment out the file removal for debugging purposes
    # os.remove(file_path)

    # Ensure the quiz result is valid JSON (or a dictionary)
    if not isinstance(quiz_result, dict):
        try:
            json_match = re.search(r"({.*})", quiz_result, re.DOTALL)
            if json_match:
                quiz_result = json.loads(json_match.group(1))
            else:
                raise ValueError("Quiz result is not a valid JSON object.")
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Error parsing quiz output: {e}")

    return {"message": "Quiz generated successfully", "quiz": quiz_result}