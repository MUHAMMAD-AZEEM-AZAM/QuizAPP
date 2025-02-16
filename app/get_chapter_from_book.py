import fitz  # PyMuPDF
from openai import OpenAI
import re
import json
import os
from dotenv import load_dotenv
load_dotenv() 

# **********Function to extract chapter information from a PDF file**********

def extract_chapter_info(pdf_path, offset=0):

    doc = fitz.open(pdf_path)
    toc = doc.get_toc()  # Get the table of contents (TOC)

    if not toc:
        print("No Table of Contents found in this PDF.")
        return []

    # Filter entries whose title includes "CHAPTER" (case-insensitive)
    chapter_entries = [entry for entry in toc if "CHAPTER" in entry[1].upper()]

    if not chapter_entries:
        print("No chapter entries found in the TOC.")
        return []

    chapters = []
    for i, entry in enumerate(chapter_entries):
        # Apply the offset to the start page
        start_page = entry[2] + offset

        # Determine the end page using the next chapter's start page, if available
        if i < len(chapter_entries) - 1:
            next_start = chapter_entries[i + 1][2] + offset
            # Only set end_page if next_start is greater than start_page
            end_page = next_start - 1 if next_start > start_page else start_page
        else:
            end_page = doc.page_count

        chapters.append({
            "title": entry[1],
            "start_page": start_page-18,
            "end_page": end_page-18
        })
    return chapters

# # Example usage:
# chapters = extract_chapter_info(pdf_path, offset=0)

# for chap in chapters:
#     print(f"Chapter: {chap['title']}")
#     print(f"Start Page: {chap['start_page']}  End Page: {chap['end_page']}\n")

# **********Refine chapter result using deepseek**********

def refine_chapter_info(chapters):
    client = OpenAI(
    base_url=os.getenv("AI_API_BASE_URL"),
    api_key=os.getenv("AI_API_KEY"),
    )

    system_message = (
        "You are an AI assistant that outputs exactly one valid JSON object with no extra text, markdown, or code formatting. "
        "Ensure that all keys and string values are enclosed in double quotes. Return only the JSON object."
    )

    user_message = (
        "Extract only the actual chapters from the following table of contents data and ignore any entries that are just noise. "
        "For example, if a chapter object has a title that is only 'Chapter 1' or 'Chapter 2' with no additional descriptive text, "
        "do not include it. Only include chapters whose title contains a proper name or subtitle (for example, 'Chapter 1: Relativity' is acceptable). "
        "Return a JSON object with a single key \"chapters\" that maps to an array of chapter objects, each with a \"title\" field and the relevant page numbers. "
        f"Here is the data: {chapters}"
    )

    response = client.chat.completions.create(
        model=os.getenv("AI_MODEL_ID"),
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )

    message = response.choices[0].message.content
    # print("Raw response:", message)


    raw_response = message  # This is the model output

    code_block_match = re.search(r"```python(.*?)```", raw_response, re.DOTALL)

    if not code_block_match:
        code_block_match = re.search(r"```python(.*)", raw_response, re.DOTALL)

    if code_block_match:
        code_block = code_block_match.group(1).strip()

    # Now, extract the JSON-like part, optionally preceded by "data ="
        json_match = re.search(r"(?:data\s*=\s*)?(\[.*\]|\{.*\})", code_block, re.DOTALL)

        if json_match:
            json_str = json_match.group(1).strip()

        # Fix common formatting issues: replace non-breaking spaces and single quotes
            json_str_fixed = json_str.replace("\xa0", " ").replace("'", "\"")
        # If needed, wrap it in brackets (if your model returns individual objects instead of an array)
            chapters = f"[{json_str_fixed}]"
        else:
            print("No JSON object found in the code block.")
            chapters = ""
    else:
        print("No Python code block found in the response.")
        chapters = ""

# Convert the chapters string to a JSON object
    try:
        chapters_obj = json.loads(chapters)
        print("Parsed JSON object:")
        filtered_chapters = [chapter for chapter in chapters_obj if chapter["start_page"] != chapter["end_page"]]

        json.dumps(filtered_chapters, indent=2, ensure_ascii=False)
        return filtered_chapters
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("The JSON string is:")
        print(chapters)


def extract_chapters_from_book(pdf_path: str) -> list:
    # Extract chapter information from a PDF file
    chapters = extract_chapter_info(pdf_path, offset=0)
    # Refine the chapter information using a language model
    refined_chapters = refine_chapter_info(chapters)
    return refined_chapters
