from fastapi import FastAPI
from dotenv import load_dotenv
from quiz import quiz_router


app = FastAPI()
load_dotenv()

app.include_router(quiz_router)