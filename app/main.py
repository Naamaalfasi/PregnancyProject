from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from app.config import settings
from app.models import UserProfile, MedicalDocument, Task, DocumentType
from app.models.chat import Conversation, ChatMessage
from app.database.mongo_client import MongoDBClient
from app.database.chroma_client import ChromaDBClient
from app.utils.pdf_processor import PDFProcessor
from app.utils.embeddings import EmbeddingGenerator
from app.agent.medical_processor import MedicalDataProcessor
from app.database.file_storage import FileStorageService
from app.database.file_processing import DocumentStatus
from app.automation.generate_test_data import TestDataGenerator
from app.agent.ChatService import ChatService
import os
from app.models.tasks import TaskCreate, TaskUpdate
from pydantic import BaseModel
import google.generativeai as genai
from app.database.DocumentService import DocumentService
from datetime import date, timedelta
from app.agent.task_manager import TaskManager
genai.configure(api_key=settings.GOOGLE_API_KEY)
_gemini = genai.GenerativeModel(settings.GEMINI_MODEL)

mongo_client = MongoDBClient()
pdf_processor = PDFProcessor()
embedding_generator = EmbeddingGenerator()
medical_processor = MedicalDataProcessor()
file_storage = FileStorageService()
chroma_client = ChromaDBClient(embedding_generator)
task_manager = TaskManager(mongo_client)
document_service = DocumentService(mongo_client, chroma_client, pdf_processor, embedding_generator, medical_processor, file_storage)
test_data_generator = TestDataGenerator(mongo_client)
chat_service = ChatService(mongo_client, _gemini)



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


@app.post("/users/{user_id}/verify-password")
async def verify_password(user_id: str, password: str):
    """Verify password"""
    return await mongo_client.verify_password(user_id, password)


@app.post("/users/{user_id}/change-password")
async def change_password(user_id: str, oldPassword: str, newPassword: str):
    """Change password"""
    return await mongo_client.change_password(user_id, oldPassword, newPassword)


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

@app.post("/users/{user_id}/tasks/standard")
async def create_standard_tasks(user_id: str):
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    tasks = await task_manager.create_standard_tasks_for_user(user.user_id)
    tasks_dicts = [t.dict() for t in tasks]
    await mongo_client.update_user_tasks(user.user_id, tasks_dicts)
    return {"message": "Standard tasks created", "tasks": tasks_dicts}
    
@app.post("/users/{user_id}/tasks", response_model=Task)
async def create_task(user_id: str, task_data: TaskCreate):
    """
    Create Task
    If a similar task already exists, return an error
    """
    tasks: List[Task] = await mongo_client.get_user_tasks(user_id)
    for t in tasks:
        if (
            t.title == task_data.title and
            t.task_type == task_data.task_type and
            t.pregnancy_week == task_data.pregnancy_week
        ):
            raise HTTPException(status_code=409, detail="Task already exists for this user in this week")
    # יצירת מטלה חדשה
    task = Task(
        task_id=str(uuid.uuid4()),
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        priority=task_data.priority,
        pregnancy_week=task_data.pregnancy_week,
        due_date=task_data.due_date,
        source=task_data.source,
        reason=task_data.reason,
        related_links=task_data.related_links,
        # שדות נוספים כמו created_at, completed וכו' יתווספו אוטומטית ע"י המודל
    )
    await mongo_client.create_task(user_id, task)
    return task

# 2. עדכון מטלה קיימת
@app.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    updated_task = await mongo_client.update_task(task_id, task_update.dict(exclude_unset=True))
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = await mongo_client.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
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


@app.post("/chat/process-chat-message")
async def chat_gemini(user_id: str, message: str):
    return await chat_service.process_chat_message(user_id, message)

@app.post("/chat/get-all-conversations-by-user-id")
async def get_all_conversations(user_id: str):
    return await chat_service.get_user_conversations(user_id)

@app.post("/chat/get-conversation-by-id")
async def get_conversation(user_id: str, conversation_id: str):
    return await chat_service.get_conversation_by_id(user_id, conversation_id)

@app.post("/chat/new-conversation")
async def new_conversation(user_id: str):
    return await chat_service.create_new_conversation(user_id)

@app.post("/chat/switch-to-conversation")
async def switch_to_conversation(user_id: str, conversation_id: str):
    return await chat_service.switch_to_conversation(user_id, conversation_id)

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
async def generate_test_data(user_count: int):
    """
    Generate test data for development and testing purposes.
    
    - **user_count**: Number of test users to create (default: 5, max: 10)
    
    This endpoint will create:
    - Test user profiles with realistic pregnancy data (tasks, documents, etc.)
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
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate test data: {str(e)}")


@app.post("/automation/cleanupTestData")
async def cleanup_test_data():
    """Cleanup test data"""
    result = await test_data_generator.cleanup_test_data()
    return {"message": "Test data cleaned up successfully", "result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


