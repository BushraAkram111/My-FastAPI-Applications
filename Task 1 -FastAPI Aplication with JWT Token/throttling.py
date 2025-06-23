from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import os

def get_user_identifier(request: Request):
    """Get user identifier from JWT token if available, otherwise fallback to IP"""
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            token = auth_header.split(" ")[1]
            return f"user_{token[:10]}"  # Use first 10 chars of token as identifier
    except:
        pass
    return get_remote_address(request)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_user_identifier,
    storage_uri=os.getenv("REDIS_URL", "memory://")  # Use Redis in production
)

# Rate limits configuration
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "10/minute")
AUTH_RATE_LIMIT = os.getenv("AUTH_RATE_LIMIT", "5/minute")
UPLOAD_RATE_LIMIT = os.getenv("UPLOAD_RATE_LIMIT", "3/minute")