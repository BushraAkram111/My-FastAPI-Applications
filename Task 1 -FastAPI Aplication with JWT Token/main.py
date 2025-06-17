# Import FastAPI and related modules for handling API requests and responses
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from conv_ret_db import SessionLocal, ConversationChatHistory, UserRegistry  # Custom DB models and session
from utils import QdrantInsertRetrievalAll  # Custom class for Qdrant operations
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from fastapi.responses import JSONResponse
from fastapi import status
import tempfile, os
import uvicorn
from dotenv import load_dotenv, find_dotenv
from passlib.context import CryptContext  # For password hashing

# JWT imports
import jwt
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 60

# Initialize OpenAI embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Initialize FastAPI app
app = FastAPI()

# JWT Helper Functions
def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return chatbot_id"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        chatbot_id: str = payload.get("chatbot_id")
        if chatbot_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return chatbot_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Signup API (No changes - remains public)
import re
import dns.resolver  # You may need to install dnspython using `pip install dnspython`

# Function to check if the email domain is valid
def is_valid_email_domain(email: str) -> bool:
    try:
        domain = email.split('@')[1]  # Get the domain part of the email
        # Check if the domain has a valid MX (Mail Exchange) record
        dns.resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False

import re

import re

@app.post("/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    chatbot_id: str = Form(...)
):
    # Regular expression for basic email validation
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

    # Validate email format
    if not re.match(email_regex, email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Password length check (minimum 8 characters)
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    session = SessionLocal()
    try:
        # Allow only up to 3 users
        if session.query(UserRegistry).count() >= 3:
            raise HTTPException(status_code=403, detail="Only 3 users allowed.")

        # Check if user already exists (by username or email)
        if session.query(UserRegistry).filter(
            (UserRegistry.username == username) | (UserRegistry.email == email)
        ).first():
            raise HTTPException(status_code=400, detail="User already exists.")

        # Hash the password before storing
        hashed_pw = pwd_context.hash(password)

        # Create and store new user
        new_user = UserRegistry(username=username, email=email, password=hashed_pw, chatbot_id=chatbot_id)
        session.add(new_user)
        session.commit()

        return {"message": "User registered successfully!"}
    finally:
        session.close()



# Login API (Updated to return JWT token)
@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    session = SessionLocal()
    try:
        # Append '@gmail.com' to the email if it doesn't already have it
        if not email.endswith("@gmail.com"):
            email = email + "@gmail.com"

        # Fetch user by email
        user = session.query(UserRegistry).filter_by(email=email).first()

        # Check if user exists and validate the password
        if not user or not pwd_context.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create JWT token
        access_token = create_access_token(data={"chatbot_id": user.chatbot_id, "email": user.email})

        return {
            "message": "Login successful", 
            "chatbot_id": user.chatbot_id,
            "access_token": access_token,
            "token_type": "bearer"
        }
    finally:
        session.close()





# Upload Multiple Files and Index to Qdrant (Protected with JWT)
@app.post("/upload-files/")
async def upload_files(
    files: list[UploadFile] = File(...), 
    chatbot_id: str = Depends(verify_token)  # JWT authentication
):
    try:
        # Initialize Qdrant helper
        qdrant_obj = QdrantInsertRetrievalAll(api_key=os.getenv("QDRANT_API_KEY"), url=os.getenv("QDRANT_URL"))
        
        # Import and set up text splitter
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        uploaded_files = []

        for file in files:
            # Temporarily save uploaded file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(await file.read())
                file_path = tmp.name

            # Use appropriate loader based on file extension
            if file.filename.endswith(".pdf"):
                from langchain_community.document_loaders import PyMuPDFLoader
                loader = PyMuPDFLoader(file_path)
            elif file.filename.endswith(".docx"):
                from langchain_community.document_loaders import UnstructuredWordDocumentLoader
                loader = UnstructuredWordDocumentLoader(file_path)
            elif file.filename.endswith(".txt"):
                from langchain.document_loaders import TextLoader
                loader = TextLoader(file_path)
            else:
                continue  # Skip unsupported files

            # Load, split, and index file content
            documents = loader.load()
            chunks = splitter.split_documents(documents)
            collection_name = f"collection_{chatbot_id}_{file.filename}"
            qdrant_obj.insertion(chunks, embeddings, collection_name)
            uploaded_files.append(file.filename)

        return {"message": "Files uploaded and indexed successfully!", "files": uploaded_files}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Ask a Question from a Specific File (Protected with JWT)
# Fixed Ask a Question from a Specific File (Protected with JWT)
@app.post("/ask/")
async def ask_question(
    question: str = Form(...),
    chatbot_id: str = Depends(verify_token)  # JWT authentication
):
    session = SessionLocal()
    try:
        # Get Qdrant client to list all collections for this user
        qdrant_obj = QdrantInsertRetrievalAll(api_key=os.getenv("QDRANT_API_KEY"), url=os.getenv("QDRANT_URL"))
        from qdrant_client import QdrantClient
        qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))
        
        # Get all collections and filter for this user's collections
        all_collections = qdrant_client.get_collections().collections
        user_collections = []
        user_files = []
        
        for collection in all_collections:
            collection_name = collection.name
            # Check if collection belongs to this user
            if collection_name.startswith(f"collection_{chatbot_id}_"):
                # Extract file name from collection name
                file_name = collection_name.replace(f"collection_{chatbot_id}_", "")
                user_collections.append(collection_name)
                user_files.append(file_name)
        
        if not user_collections:
            return JSONResponse(
                content={"error": "No files found. Please upload files first."}, 
                status_code=404
            )
        
        # Search through all user collections and find the best match
        best_answer = ""
        best_score = 0
        source_file = ""
        all_results = []
        
        for i, collection_name in enumerate(user_collections):
            try:
                # Get retriever for this collection
                retriever = qdrant_obj.retrieval(collection_name=collection_name, embeddings=embeddings)
                relevant_docs = retriever.as_retriever().get_relevant_documents(question)
                
                if relevant_docs:
                    # Combine document content into context
                    context_text = "\n".join([doc.page_content for doc in relevant_docs])
                    
                    # Create and format prompt
                    prompt_template = PromptTemplate.from_template(
                        """
                        You are a helpful AI assistant. Answer the user's question based on the provided context from their uploaded documents.

                        IMPORTANT INSTRUCTIONS:
                        1. Use the information from the context to provide a comprehensive answer
                        2. If you find relevant information, provide a detailed response
                        3. Quote specific parts from the documents when relevant
                        4. If the exact answer isn't found but related information exists, mention the related information
                        5. Always try to be helpful and extract any relevant details from the context
                        6. Mention which document(s) the information comes from
                        Context:
                        {context}

                        Question: {question}

                        Answer:
                        """
                    )
                    prompt = prompt_template.format(context=context_text, question=question)
                    
                    # Use ChatOpenAI to generate response
                    model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0)
                    response = model.invoke(prompt)
                    
                    # Simple scoring based on response length and relevance
                    # (You can implement more sophisticated scoring if needed)
                    response_text = response.content.strip()
                    if "No relevant information found" not in response_text and len(response_text) > 20:
                        # Score based on response quality (simple heuristic)
                        score = len(response_text) + len(context_text) / 100
                        
                        all_results.append({
                            "file": user_files[i],
                            "answer": response_text,
                            "score": score,
                            "context_length": len(context_text)
                        })
                        
                        if score > best_score:
                            best_score = score
                            best_answer = response_text
                            source_file = user_files[i]
            
            except Exception as e:
                # Skip this collection if there's an error
                print(f"Error processing collection {collection_name}: {str(e)}")
                continue
        
        if not best_answer:
            return {
                "message": "No relevant information found in any uploaded files.",
                "searched_files": user_files,
                "answer": "I couldn't find relevant information to answer your question in any of your uploaded files."
            }
        
        # Save the conversation to DB
        session.add(ConversationChatHistory(
            chatbot_id=chatbot_id, 
            query=question, 
            response=f"[From: {source_file}] {best_answer}"
        ))
        session.commit()
        
        return {
            "message": "Answer generated successfully!",
            "source_file": source_file,
            "answer": best_answer,
            "searched_files": user_files,
            "total_files_searched": len(user_files),
            "alternative_answers": [
                {"file": result["file"], "answer": result["answer"][:200] + "..." if len(result["answer"]) > 200 else result["answer"]}
                for result in sorted(all_results, key=lambda x: x["score"], reverse=True)[1:3]  # Top 2 alternatives
            ] if len(all_results) > 1 else []
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        session.close()
# Run FastAPI App with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8006, reload=True)