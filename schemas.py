from pydantic import BaseModel

class TokenData(BaseModel):
    chatbot_id: str
    email: str
    user_id: int
    username: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str

class LoginResponse(BaseModel):
    message: str
    chatbot_id: str
    username: str
    access_token: str
    token_type: str

class FileUploadResponse(BaseModel):
    message: str
    files: list[str]

class QuestionResponse(BaseModel):
    message: str
    source_file: str
    answer: str
    searched_files: list[str] = []
    total_files_searched: int = 0
    alternative_answers: list[dict] = []

class Conversation(BaseModel):
    id: int
    query: str
    response: str
    created_at: str = None

class ConversationList(BaseModel):
    conversations: list[Conversation]
    pagination: dict