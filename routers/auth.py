from fastapi import APIRouter, HTTPException, Form, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
import uuid
import re
import os
from dotenv import load_dotenv

from conv_ret_db import SessionLocal, UserRegistry
from schemas import TokenData, UserCreate, UserResponse, LoginResponse

load_dotenv()

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 60

def generate_unique_chatbot_id():
    """Generate a unique chatbot ID using UUID"""
    return f"chatbot_{uuid.uuid4().hex[:16]}"

def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=UserResponse)
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    session = SessionLocal()
    try:
        if session.query(UserRegistry).count() >= 3:
            raise HTTPException(status_code=403, detail="Only 3 users allowed.")

        if session.query(UserRegistry).filter(
            (UserRegistry.username == username) | (UserRegistry.email == email)
        ).first():
            raise HTTPException(status_code=400, detail="User already exists.")

        hashed_pw = pwd_context.hash(password)
        new_user = UserRegistry(
            username=username, 
            email=email, 
            password=hashed_pw, 
            chatbot_id=""
        )
        session.add(new_user)
        session.commit()

        return {
            "username": username,
            "email": email
        }
    finally:
        session.close()

@router.post("/login", response_model=LoginResponse)
async def login(email: str = Form(...), password: str = Form(...)):
    session = SessionLocal()
    try:
        user = session.query(UserRegistry).filter_by(email=email).first()

        if not user or not pwd_context.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        session_chatbot_id = generate_unique_chatbot_id()
        access_token = create_access_token(data={
            "chatbot_id": session_chatbot_id, 
            "email": user.email,
            "user_id": user.id,
            "username": user.username
        })

        return {
            "message": "Login successful", 
            "chatbot_id": session_chatbot_id,
            "username": user.username,
            "access_token": access_token,
            "token_type": "bearer"
        }
    finally:
        session.close()