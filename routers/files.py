from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
import tempfile
import os
from typing import List

from conv_ret_db import SessionLocal, ConversationChatHistory
from utils import QdrantInsertRetrievalAll
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient

from dependencies import verify_token

router = APIRouter()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/upload-files/")
async def upload_files(
    files: List[UploadFile] = File(...), 
    auth_data: dict = Depends(verify_token)  # JWT authentication
):
    chatbot_id = auth_data["chatbot_id"]
    try:
        # Initialize Qdrant helper
        qdrant_obj = QdrantInsertRetrievalAll(api_key=os.getenv("QDRANT_API_KEY"), url=os.getenv("QDRANT_URL"))
        
        # Import and set up text splitter
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

@router.post("/ask/")
async def ask_question(
    question: str = Form(...),
    file_name: str = Form(None),  # Made file_name optional
    auth_data: dict = Depends(verify_token)  # JWT authentication
):
    chatbot_id = auth_data["chatbot_id"]
    session = SessionLocal()
    try:
        qdrant_obj = QdrantInsertRetrievalAll(api_key=os.getenv("QDRANT_API_KEY"), url=os.getenv("QDRANT_URL"))
        qdrant_client = QdrantClient(url=os.getenv("QDRANT_URL"), api_key=os.getenv("QDRANT_API_KEY"))

        if file_name:
            # If file_name is provided, search only in that specific file
            collection_name = f"collection_{chatbot_id}_{file_name}"
            all_collections = qdrant_client.get_collections().collections
            user_collections = [col.name for col in all_collections if col.name.startswith(f"collection_{chatbot_id}_")]
            user_files = [col_name.replace(f"collection_{chatbot_id}_", "") for col_name in user_collections]

            if collection_name not in user_collections:
                return JSONResponse(
                    content={"error": f"File '{file_name}' not found for this user. Available files: {', '.join(user_files)}"}, 
                    status_code=404
                )
            
            retriever = qdrant_obj.retrieval(collection_name=collection_name, embeddings=embeddings)
            relevant_docs = retriever.as_retriever().get_relevant_documents(question)
            
            if not relevant_docs:
                return {
                    "message": f"No relevant information found in '{file_name}'.",
                    "source_file": file_name,
                    "answer": f"I couldn't find relevant information to answer your question in '{file_name}'."
                }
            
            context_text = "\n".join([doc.page_content for doc in relevant_docs])
            prompt_template = PromptTemplate.from_template(
                """
                You are a helpful AI assistant. Answer the user's question based on the provided context from their recently uploaded documents.

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
            model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0)
            response = model.invoke(prompt)
            response_text = response.content.strip()
            
            session.add(ConversationChatHistory(
                chatbot_id=chatbot_id, 
                query=question, 
                response=f"[From: {file_name}] {response_text}"
            ))
            session.commit()
            
            return {
                "message": "Answer generated successfully!",
                "source_file": file_name,
                "answer": response_text
            }

        else:
            # If no file_name is provided, search across all user's files
            all_collections = qdrant_client.get_collections().collections
            user_collections = []
            user_files = []
            
            for collection in all_collections:
                collection_name = collection.name
                if collection_name.startswith(f"collection_{chatbot_id}_"):
                    file_name_from_collection = collection_name.replace(f"collection_{chatbot_id}_", "")
                    user_collections.append(collection_name)
                    user_files.append(file_name_from_collection)
            
            if not user_collections:
                return JSONResponse(
                    content={"error": "No files found. Please upload files first."}, 
                    status_code=404
                )
            
            best_answer = ""
            best_score = 0
            source_file = ""
            all_results = []
            
            for i, collection_name in enumerate(user_collections):
                try:
                    retriever = qdrant_obj.retrieval(collection_name=collection_name, embeddings=embeddings)
                    relevant_docs = retriever.as_retriever().get_relevant_documents(question)
                    
                    if relevant_docs:
                        context_text = "\n".join([doc.page_content for doc in relevant_docs])
                        prompt_template = PromptTemplate.from_template(
                            """
                            You are a helpful AI assistant. Answer the user's question based on the provided context from their recently uploaded documents.

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
                        model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY, temperature=0)
                        response = model.invoke(prompt)
                        response_text = response.content.strip()
                        
                        if "No relevant information found" not in response_text and len(response_text) > 20:
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
                    print(f"Error processing collection {collection_name}: {str(e)}")
                    continue
            
            if not best_answer:
                return {
                    "message": "No relevant information found in any uploaded files.",
                    "searched_files": user_files,
                    "answer": "I couldn't find relevant information to answer your question in any of your uploaded files."
                }
            
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