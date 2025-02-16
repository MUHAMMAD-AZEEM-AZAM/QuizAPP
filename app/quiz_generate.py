import fitz
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv() 

from get_chapter_from_book import extract_chapters_from_book
from prompt import question_generate_prompt

client = OpenAI(
    base_url=os.getenv("AI_API_BASE_URL"),
    api_key=os.getenv("AI_API_KEY"),
)

def generate_quiz_from_book(pdf_path: str) -> dict:

    try:
       chapters=extract_chapters_from_book(pdf_path)
       questions=generate_question_against_chapter(chapters[0],pdf_path)
       print(questions)

    except Exception as e:
        raise Exception(f"Error reading PDF file: {e}")
    
    # Dummy quiz output (replace with your actual quiz generation logic)
   
    return chapters



def generate_question_against_chapter(chapter: dict,pdf_path) -> dict:
    # Dummy question generation logic
    questions = {}
    chapter_text=extract_chapter_text(pdf_path, chapter["start_page"], chapter["end_page"])
    quiz_output = generate_quiz(chapter_text)
    try:
        quiz_json = json.loads(quiz_output)
        print(f"Valid JSON output received for {chapter['title']}:")
        json.dumps(quiz_json, indent=2, ensure_ascii=False)
        questions=quiz_json
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {chapter['title']}: {e}")
        print("Received output:", quiz_output)
    return questions



# --- Function to Extract Chapter Text from a PDF ---
def extract_chapter_text(pdf_path, start_page, end_page):
    """
    Extracts and returns text from the PDF between start_page and end_page.
    Note: PDF pages are 1-indexed in our input; PyMuPDF uses 0-indexed pages.
    """
    doc = fitz.open(pdf_path)
    chapter_text = ""
    for page_number in range(start_page - 1, end_page):
        page = doc.load_page(page_number)
        chapter_text += page.get_text("text") + "\n"
    doc.close()
    return chapter_text

# --- Function to Truncate Text to a Given Number of Words ---
def truncate_text(text, max_words=150):
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words])
    return text

# --- Function to Generate Quiz Using DeepSeek via OpenAI Library ---
def generate_quiz(chapter_text):

    # Further truncate the chapter text to reduce input token count
    chapter_text = truncate_text(chapter_text, max_words=150)

    detailed_prompt =question_generate_prompt + chapter_text

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL_ID"),  # Use the appropriate DeepSeek model
        messages=[
            {"role": "system", "content": "You are a professional quiz generator AI."},
            {"role": "user", "content": detailed_prompt},
        ],
        max_tokens=4000,  # Reduced output token limit for testing
        temperature=0.7
    )
    return response.choices[0].message.content
