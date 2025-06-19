from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv, find_dotenv

# Import routers
from routers import auth, files, users

# Load environment variables
load_dotenv(find_dotenv())

# Initialize FastAPI app
app = FastAPI(title="Document QA API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(files.router, prefix="/files", tags=["Files"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# Run FastAPI App with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006, reload=True)