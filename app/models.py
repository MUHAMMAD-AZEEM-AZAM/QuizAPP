from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Union
import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

# --- Question Models ---
class MCQ(BaseModel):
    id: str = Field(default_factory=generate_uuid, description="Unique id for the MCQ")
    question: str = Field(..., description="The text of the MCQ")
    options: Dict[str, str] = Field(..., description="Options as a dictionary (A, B, C, D)")
    correct_answer: str = Field(..., description="The correct option key (e.g., 'A')")
    hint: str = Field(..., description="A hint for the question")
    question_type: Literal["mcq"] = "mcq"

class ShortQuestion(BaseModel):
    id: str = Field(default_factory=generate_uuid, description="Unique id for the short question")
    question: str = Field(..., description="The text of the short answer question")
    solution: str = Field(..., description="The appropriate short answer")
    question_type: Literal["short"] = "short"

class LongQuestion(BaseModel):
    id: str = Field(default_factory=generate_uuid, description="Unique id for the long question")
    question: str = Field(..., description="The text of the long answer question")
    solution: str = Field(..., description="The appropriate long answer")
    question_type: Literal["long"] = "long"

# --- Quiz Model (for a chapter) ---
class Quiz(BaseModel):
    title: str = Field(..., description="Title of the quiz (e.g., chapter title)")
    chapter: str = Field(..., description="The chapter for which the quiz is generated")
    mcqs: List[MCQ] = Field(..., description="List of MCQ questions")
    short: List[ShortQuestion] = Field(..., description="List of short answer questions")
    long: List[LongQuestion] = Field(..., description="List of long answer questions")

# --- Chapter Model ---
class Chapter(BaseModel):
    chapter_number: int = Field(..., description="Chapter number")
    title: str = Field(..., description="Chapter title")
    quiz: Quiz = Field(..., description="Quiz generated for this chapter")

# --- Book Model ---
class Book(BaseModel):
    id: str = Field(default_factory=generate_uuid, description="Unique id for the book")
    user_id: str = Field(..., description="ID of the user who uploaded the book")
    book_name: str = Field(..., description="Name of the book")
    chapters: List[Chapter] = Field(..., description="List of chapters with generated quizzes")
