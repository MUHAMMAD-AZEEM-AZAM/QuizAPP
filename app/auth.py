from fastapi import APIRouter, HTTPException, Depends
from database import users_collection
from pydantic import BaseModel
from passlib.context import CryptContext
# import jwt
import jwt
from datetime import datetime, timedelta

# JWT Secret Key
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Pydantic Model
class User(BaseModel):
    username: str
    password: str

auth_router = APIRouter()

@auth_router.post("/auth_user")
async def just_login(user: User):
    existing_user =await users_collection.find_one({"username": user.username})
    # if not exiting user then register and provide token
    auth_type = "login"
        
    if existing_user:
        if not verify_password(user.password, existing_user["password"]):
            raise HTTPException(status_code=400, detail="Invalid credentials")
    else:
        hashed_password = hash_password(user.password)
        await users_collection.insert_one({"username": user.username, "password": hashed_password})
        auth_type = "register"
    
    # Generate JWT Token
    token = create_access_token({"sub": user.username})
    return {"token": token, "token_type": "bearer", "auth_type": auth_type, "statusCode": 200, "message": f"User {auth_type} successful", "role": "user"}
