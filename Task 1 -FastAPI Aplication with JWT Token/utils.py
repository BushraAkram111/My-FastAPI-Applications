# Import document loaders for handling PDF, Word, and text files
from langchain_community.document_loaders import PyMuPDFLoader, UnstructuredWordDocumentLoader
from langchain.document_loaders import TextLoader

# Import text splitter to break documents into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import OpenAI embeddings to convert text into vectors
from langchain_openai import OpenAIEmbeddings 

# Import OS module (optional, used for file paths or environment variables)
import os

# Import Qdrant client and LangChain's Qdrant integration
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore, Qdrant

# Define a class to handle both insertion and retrieval from Qdrant
class QdrantInsertRetrievalAll:
    def __init__(self, api_key, url):
        # Store the Qdrant API key and URL
        self.url = url 
        self.api_key = api_key

    # Method to insert documents into Qdrant vector store
    def insertion(self, text, embeddings, collection_name):
        qdrant = QdrantVectorStore.from_documents(
            text,  # List of documents or text chunks
            embeddings,  # Embedding model used to convert text to vectors
            url=self.url,
            prefer_grpc=True,  # Prefer using gRPC for better performance
            api_key=self.api_key,
            collection_name=collection_name,  # Name of the Qdrant collection
            force_recreate=True  # Overwrite collection if it already exists
        )
        return qdrant  # Return the Qdrant vector store object

    # Method to retrieve the vector store for querying
    def retrieval(self, collection_name, embeddings):
        qdrant_client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
        )
        # Connect to the existing Qdrant collection
        qdrant_store = Qdrant(qdrant_client, collection_name=collection_name, embeddings=embeddings)
        return qdrant_store  # Return the Qdrant store object for retrieval
