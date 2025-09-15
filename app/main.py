from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.config import settings
from app.models import UserProfile, MedicalDocument, Task, ChatRequest, ChatResponse, DocumentType
from app.database.mongo_client import MongoDBClient
from app.database.chroma_client import ChromaDBClient
from app.utils.pdf_processor import PDFProcessor
from app.utils.embeddings import EmbeddingGenerator
from app.agent.medical_processor import MedicalDataProcessor
from app.database.file_storage import FileStorageService
from app.database.file_processing import DocumentStatus
from app.automation.generate_test_data import TestDataGenerator
import os
from pydantic import BaseModel
import google.generativeai as genai
from app.database.DocumentService import DocumentService

mongo_client = MongoDBClient()
pdf_processor = PDFProcessor()
embedding_generator = EmbeddingGenerator()
medical_processor = MedicalDataProcessor()
file_storage = FileStorageService()

chroma_client = ChromaDBClient(embedding_generator)

document_service = DocumentService(mongo_client, chroma_client, pdf_processor, embedding_generator, medical_processor, file_storage)

test_data_generator = TestDataGenerator(mongo_client)

# Initialize FastAPI app
app = FastAPI(
    title="Pregnancy Agent API",
    description="AI-driven pregnancy assistant with RAG and Agent capabilities",
    version="1.0.0"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    await mongo_client.connect()
    await chroma_client.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await mongo_client.close()
    await chroma_client.close()


# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Pregnancy Agent API is running!", "status": "healthy"}


# User Profile Endpoints
@app.post("/users", response_model=UserProfile)
async def create_user_profile(profile: UserProfile): 
    return await mongo_client.create_user_profile(profile)


@app.get("/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    profile = await mongo_client.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile


@app.put("/users/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, profile: UserProfile):
    """Update user profile"""
    profile.user_id = user_id
    profile.updated_at = datetime.utcnow()
    
    updated_profile = await mongo_client.update_user_profile(user_id, profile)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return updated_profile


# Medical Documents Endpoints
@app.post("/users/{user_id}/documents")
async def upload_medical_document( user_id: str, file: UploadFile = File(...), document_type: DocumentType = DocumentType.OTHER ):
    """Upload and process medical document"""
    # Validate user exists
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    return await document_service.create_document(user_id, file, document_type)
    
@app.post("/users/{user_id}/documents/{document_id}/process")
async def process_document_background(user_id: str, document_id: str):
    """Process a document in the background"""
    document = await mongo_client.get_medical_document(user_id, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.status != DocumentStatus.UPLOADED:
        raise HTTPException(status_code=400, detail="Document is not in uploaded state")

    # Initialize processors
    await mongo_client.update_document_status(user_id, document_id, DocumentStatus.PROCESSING)

    result = await document_service.process_document(user_id, document_id)

    await mongo_client.update_document_status(user_id, document_id, DocumentStatus.COMPLETED)

    return result

@app.post("/users/{user_id}/documents/full-flow")
async def DocumentFullFlow(user_id: str, file: UploadFile = File(...), document_type: DocumentType = DocumentType.OTHER):
    try:
        result = await document_service.document_upload_and_process(user_id, file, document_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/users/{user_id}/documents", response_model=List[MedicalDocument])
async def get_user_documents(user_id: str):
    """Get all medical documents for a user"""
    documents = await mongo_client.get_user_documents(user_id)
    return documents


# Tasks Endpoints
@app.post("/users/{user_id}/tasks", response_model=Task)
async def create_task(user_id: str, task: Task):
    """Create a new task for user"""
    task.task_id = str(uuid.uuid4())
    task.user_id = user_id
    task.created_at = datetime.utcnow()
    
    await mongo_client.create_task(task)
    return task


@app.get("/users/{user_id}/tasks", response_model=List[Task])
async def get_user_tasks(user_id: str, completed: Optional[bool] = None):
    """Get tasks for user with optional completion filter"""
    tasks = await mongo_client.get_user_tasks(user_id, completed)
    return tasks

@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, task_update: dict):
    """Update task (mark as completed, change priority, etc.)"""
    updated_task = await mongo_client.update_task(task_id, task_update)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    success = await mongo_client.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@app.delete("/users/{user_id}/documents/{document_id}")
async def delete_document(user_id: str, document_id: str):
    """Delete a medical document and its associated file"""
    # Get user profile to find the document
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # Find the document to delete
    document_to_delete = None
    for doc in user.medical_documents:
        if doc.document_id == document_id:
            document_to_delete = doc
            break
    
    if not document_to_delete:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete the file from file system
    file_deleted = file_storage.delete_file(document_to_delete.file_path)
    
    # Remove document from user profile
    document_removed = await mongo_client.remove_medical_document(user_id, document_id)
    
    if file_deleted and document_removed:
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document completely")



CHAT_CONTEXTS = {}

genai.configure(api_key=settings.GOOGLE_API_KEY)
_gemini = genai.GenerativeModel(settings.GEMINI_MODEL)

@app.post("/chat/test")
async def test_chat(user_id: str, message: str):
    # Fetch the user profile from DB using user_id
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    session_id = user_id or "default"
    context = CHAT_CONTEXTS.get(session_id, "")
    prompt_profile = user.model_dump_json(exclude_none=True)

    prompt = f"""
Answer the question below.

USER PROFILE: {prompt_profile}

HERE is the conversation history: {context}

Question: {message}

IMPORTANT:
- Use the UserProfile ONLY to personalize the answer.
- Consider the user's pregnancy week, medical conditions, and allergies
- Provide safe, evidence-based pregnancy advice
- If medical concerns arise, suggest consulting a healthcare provider
- Be supportive and informative
- If the private context is missing or not relevant, answer from your general medical knowledge.
- Prioritize safety; avoid diagnoses; suggest consulting a healthcare provider when appropriate.

Answer:
""".strip()

    try:
        resp = _gemini.generate_content(prompt)
        answer = resp.text if hasattr(resp, "text") else str(resp)
    except Exception as e:
        # Handle quota errors gracefully
        err_msg = str(e)
        if "429" in err_msg or "ResourceExhausted" in err_msg:
            raise HTTPException(status_code=429, detail="Gemini quota exceeded. Please try again later or switch to a lower-cost model.")
        raise HTTPException(status_code=500, detail="Gemini error: " + err_msg)

    context += f"\nUser: {message}\nAI: {answer}"
    CHAT_CONTEXTS[session_id] = context
    return {"response": answer}


# Pregnancy Timeline Endpoints
@app.get("/users/{user_id}/timeline")
async def get_pregnancy_timeline(user_id: str):
    """Get pregnancy timeline with upcoming checkups and tasks"""
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # TODO: Generate timeline based on pregnancy week
    # - Upcoming medical checkups
    # - Important milestones
    # - Recommended tasks
    
    timeline = {
        "current_week": user.pregnancy_week,
        "due_date": user.due_date,
        "upcoming_checkups": [],
        "milestones": [],
        "recommendations": []
    }
    
    return timeline


@app.get("/users", response_model=List[UserProfile])
async def get_all_users():
    """Get all user profiles"""
    users = await mongo_client.get_all_users()
    return users


@app.post("/users/update-all-users-calculated-fields")
async def update_all_users_calculated_fields():
    """Update all users calculated fields"""
    result = await mongo_client.update_all_users_calculated_fields()
    return {"message": "All users calculated fields updated successfully", "result": result}


@app.post("/automation/generateDataForTests")
async def generate_test_data(user_count: int = 5):
    """
    Generate test data for development and testing purposes.
    
    - **user_count**: Number of test users to create (default: 5, max: 10)
    
    This endpoint will create:
    - Test user profiles with realistic pregnancy data
    - Sample tasks for each user
    - Sample medical documents for each user
    """
    try:
        # Generate test data
        result = await test_data_generator.generate_complete_test_data(user_count)
        
        return {
            "message": "Test data generated successfully!",
            "summary": {
                "users_created": result["users_created"],
                "documents_created": result["documents_created"],
                "generated_at": result["generated_at"]
            },
            "test_user_ids": result["user_ids"],
            "details": {
                "documents_by_user": result["documents_by_user"]
            },
            "testing_endpoints": {
                "get_all_users": "GET /users",
                "get_user_profile": "GET /users/{user_id}",
                "get_user_documents": "GET /users/{user_id}/documents",
                "update_user": "PUT /users/{user_id}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate test data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


