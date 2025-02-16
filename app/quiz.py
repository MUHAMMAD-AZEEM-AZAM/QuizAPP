import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from quiz_generate import generate_quiz_from_book
from database import books_collection  # Used if needed elsewhere
from dotenv import load_dotenv

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
    return {"message": "Book quiz generated and stored successfully", "book": book_quiz}