# app/main.py
from fastapi import FastAPI
from quiz import quiz_router

app = FastAPI(title="Quiz Generator API")

app.include_router(quiz_router, prefix="/api")
