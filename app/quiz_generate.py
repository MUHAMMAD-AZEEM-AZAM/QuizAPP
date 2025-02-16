import re
import json
import fitz  # PyMuPDF
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from prompt import question_generate_prompt
from get_chapter_from_book import extract_chapters_from_book  # Your chapter extraction function
from json_repair import repair_json


load_dotenv()

client = OpenAI(
    base_url=os.getenv("AI_API_BASE_URL"),
    api_key=os.getenv("AI_API_KEY"),
)

def extract_chapter_text(pdf_path: str, start_page: int, end_page: int) -> str:
    doc = fitz.open(pdf_path)
    chapter_text = ""
    for page_number in range(start_page - 1, end_page):
        page = doc.load_page(page_number)
        chapter_text += page.get_text("text") + "\n"
    doc.close()
    return chapter_text

def truncate_text(text: str, max_words: int = 60) -> str:
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text

def generate_quiz(chapter_text: str) -> str:
    # Further truncate chapter text
    chapter_text = truncate_text(chapter_text, max_words=80)
    detailed_prompt = question_generate_prompt + "\n\n" + chapter_text + "\n\nPlease finish the JSON output completely."
    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL_ID"),  # e.g., "deepseek-ai/deepseek-llm-67b-chat"
        messages=[
            {"role": "system", "content": "You are a professional quiz generator AI."},
            {"role": "user", "content": detailed_prompt},
        ],
        max_tokens=3000,
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_quiz_for_chapter(chapter: dict, pdf_path: str) -> dict:
    """
    Given a chapter dictionary, generate the quiz using the DeepSeek model.
    Retry up to 3 times if JSON parsing fails.
    """
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        chapter_text = extract_chapter_text(pdf_path, chapter["start_page"], chapter["end_page"])
        quiz_output = generate_quiz(chapter_text)
        print(f"Quiz output for {chapter['title']} (try {retry_count+1}):", quiz_output)
        try:
            json_match = re.search(r"({.*})", quiz_output, re.DOTALL)
            if json_match:
                quiz_json_str = json_match.group(1)
            else:
                quiz_json_str = quiz_output
                
            good_json_string = repair_json(quiz_json_str)
            quiz_json = json.loads(good_json_string )
            return quiz_json
        except json.JSONDecodeError as e:
            retry_count += 1
            print(f"Error parsing quiz output for {chapter.get('title')}: {e}. Retrying ({retry_count}/{max_retries})...")
            time.sleep(1)
    raise Exception(f"Failed to parse quiz output for {chapter.get('title')} after {max_retries} retries.")

async def generate_quiz_from_book(pdf_path: str, user_id: str, book_name: str) -> dict:
    """
    Processes the PDF: extracts chapters, and for each chapter (limited to the first two for testing):
      - Generates the quiz for the chapter.
      - Immediately stores the chapter quiz in the 'chapters' collection.
      - Updates the Book object with the stored chapter information.
    Finally, stores the complete Book object in the 'books' collection.
    """
    from database import chapters_collection, books_collection

    chapters_data = extract_chapters_from_book(pdf_path)
    # Limit to the first two chapters for testing
    chapters_data = chapters_data
    stored_chapters = []
    
    for i, chapter in enumerate(chapters_data):
        print(f"Processing {chapter['title']}")
        quiz_data = generate_quiz_for_chapter(chapter, pdf_path)
        chapter_obj = {
            "chapter_number": i + 1,
            "title": chapter["title"],
            "quiz": quiz_data
        }
        # Store this chapter in the DB
        result = await chapters_collection.insert_one(chapter_obj)
        chapter_obj["_id"] = str(result.inserted_id)
        stored_chapters.append(chapter_obj)
    
    # Create a Book object that references all stored chapters
    book_obj = {
        "user_id": user_id,
        "book_name": book_name,
        "chapters": stored_chapters
    }
    result = await books_collection.insert_one(book_obj)
    book_obj["_id"] = str(result.inserted_id)
    return book_obj
