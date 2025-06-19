from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os

security = HTTPBearer()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        chatbot_id: str = payload.get("chatbot_id")
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        username: str = payload.get("username")
        
        if chatbot_id is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {
            "chatbot_id": chatbot_id,
            "user_id": user_id,
            "email": email,
            "username": username
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")