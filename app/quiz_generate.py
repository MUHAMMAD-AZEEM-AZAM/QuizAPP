# app/quiz_generate.py
import re
import json
import fitz  # PyMuPDF
import os
from openai import OpenAI
from dotenv import load_dotenv
from prompt import question_generate_prompt
from get_chapter_from_book import extract_chapters_from_book  # Your chapter extraction function

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

def truncate_text(text: str, max_words: int = 100) -> str:
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text

def generate_quiz(chapter_text: str) -> str:
    """
    Uses the DeepSeek model (via OpenAI API) to generate a quiz based on the chapter text.
    The prompt instructs the model to output a valid JSON object with keys: 'mcqs', 'short', and 'long'.
    A custom stop marker is used to help ensure complete JSON output.
    """
    # Further truncate the chapter text to reduce input tokens (adjust max_words as needed)
    chapter_text = truncate_text(chapter_text, max_words=50)
    
    # Construct the prompt; add a unique marker at the end that the model should output
    detailed_prompt = (
        question_generate_prompt + "\n\n" + chapter_text +
        "\n\nPlease finish the JSON output and then output the marker: ##END_JSON##"
    )

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL_ID"),  # e.g., "deepseek-ai/deepseek-llm-67b-chat"
        messages=[
            {"role": "system", "content": "You are a professional quiz generator AI."},
            {"role": "user", "content": detailed_prompt},
        ],
        max_tokens=3000,  # Adjust if needed
        temperature=0.7,
        stop=["##END_JSON##"]
    )
    output = response.choices[0].message.content.strip()
    print("This is output",output)
    # Remove the custom stop marker if present
    if output.endswith("##END_JSON##"):
        output = output.replace("##END_JSON##", "").strip()
    return output

def generate_quiz_for_chapter(chapter: dict, pdf_path: str) -> dict:
    chapter_text = extract_chapter_text(pdf_path, chapter["start_page"], chapter["end_page"])
    quiz_output = generate_quiz(chapter_text)
    try:
        json_match = re.search(r"({.*})", quiz_output, re.DOTALL)
        if json_match:
            quiz_json_str = json_match.group(1)
        else:
            quiz_json_str = quiz_output
        quiz_json = json.loads(quiz_json_str)
        return quiz_json
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing quiz output for {chapter.get('title')}: {e}. Received output: {quiz_output}")

def generate_quiz_from_book(pdf_path: str, user_id: str, book_name: str) -> dict:
    """
    Processes the given PDF to extract chapters, generates quizzes for every chapter,
    and constructs a Book object with the user_id, book_name, and list of chapters.
    Each chapter contains its chapter number (based on its position), title, and generated quiz.
    """
    chapters_data = extract_chapters_from_book(pdf_path)
    book_chapters = []
    
    for i, chapter in enumerate(chapters_data):
        quiz_data = generate_quiz_for_chapter(chapter, pdf_path)
        
        chapter_obj = {
            "chapter_number": i + 1,  # Using the position (starting at 1)
            "title": chapter["title"],
            "quiz": quiz_data
        }
        print("This is chapter object",chapter_obj)
        book_chapters.append(chapter_obj)
    
    book_obj = {
        "user_id": user_id,
        "book_name": book_name,
        "chapters": book_chapters
    }
    print("This is book object",book_obj)
    return book_obj

