from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal, Union

# ---------------------------
# Base class for questions
# ---------------------------
class BaseQuestion(BaseModel):
    question: str = Field(..., description="The text of the question")

# ---------------------------
# Models for each question type
# ---------------------------
class MCQ(BaseModel):
    question: str = Field(..., description="The text of the MCQ")
    options: Dict[str, str] = Field(..., description="Options as a dictionary (A, B, C, D)")
    correct_answer: str = Field(..., description="The correct option key, e.g., 'A'")
    hint: str = Field(..., description="A hint for the question")

class ShortQuestion(BaseModel):
    question: str = Field(..., description="The short answer question")
    solution: str = Field(..., description="The appropriate short answer")

class LongQuestion(BaseModel):
    question: str = Field(..., description="The long answer question")
    solution: str = Field(..., description="The appropriate long answer")

class Quiz(BaseModel):
    title: str = Field(..., description="Title of the quiz (e.g., chapter title)")
    chapter: str = Field(..., description="The chapter for which this quiz is generated")
    mcqs: List[MCQ] = Field(..., description="List of MCQ questions")
    short: List[ShortQuestion] = Field(..., description="List of short answer questions")
    long: List[LongQuestion] = Field(..., description="List of long answer questions")

# ---------------------------
# Discriminated union for questions
# ---------------------------
Question = Union[MCQ, ShortQuestion, LongQuestion]

# ---------------------------
# Chapter/Book Models
# ---------------------------
class Chapter(BaseModel):
    chapter_number: int
    title: str
    questions: List[Question]

class Book(BaseModel):
    title: str
    author: Optional[str] = None
    chapters: List[Chapter]
