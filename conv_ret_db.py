# Import required SQLAlchemy modules for ORM and database connection
from sqlalchemy import Column, Integer, String, Text, create_engine, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker

# Import OS module and dotenv for loading environment variables
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Fetch PostgreSQL credentials from environment variables
PG_USER_NAME = os.getenv("PG_USER_NAME")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_NAME = os.getenv("PG_NAME")

# Create the full database connection URL
DATABASE_URL = f"postgresql://{PG_USER_NAME}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_NAME}"

# Create the SQLAlchemy engine for database connection
engine = create_engine(DATABASE_URL)

# Create a session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Define the user registry table model
class UserRegistry(Base):
    __tablename__ = "user_registry"  # Table name in the database

    id = Column(Integer, primary_key=True, index=True)  # Primary key
    username = Column(String(100), unique=True, nullable=False)  # Unique username
    email = Column(String(100), unique=True, nullable=False)  # Unique email address
    password = Column(Text, nullable=False)  # Encrypted password
    chatbot_id = Column(String(100), unique=True, nullable=False)  # Unique chatbot identifier

# Define the conversation history table model
class ConversationChatHistory(Base):
    __tablename__ = "conversation_chain"  # Table name in the database

    id = Column(BigInteger, primary_key=True, index=True)  # Primary key with large integer type
    chatbot_id = Column(String, nullable=False)  # Related chatbot identifier
    query = Column(Text, nullable=False)  # User's input/query
    response = Column(Text, nullable=False)  # Bot's response
