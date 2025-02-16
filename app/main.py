# app/main.py
from fastapi import FastAPI
from quiz import quiz_router
from dotenv import load_dotenv

app = FastAPI(title="Quiz Generator API")

app.include_router(quiz_router, prefix="/api")
from auth import auth_router
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()
app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(quiz_router)
app.include_router(auth_router)
