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

# Initialize database clients
mongo_client = MongoDBClient()
chroma_client = ChromaDBClient()

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
    await mongo_client.create_user_profile(profile)
    return profile

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
async def upload_medical_document(
    user_id: str,
    file: UploadFile = File(...),
    document_type: DocumentType = DocumentType.OTHER
):
    """Upload and process medical document"""
    # Validate user exists
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Initialize processors
    pdf_processor = PDFProcessor()
    embedding_generator = EmbeddingGenerator()
    

    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Extract text and process document
    extracted_text = pdf_processor.extract_text_from_pdf(file_content)
    chunks = pdf_processor.chunk_text(extracted_text)
    medical_data = pdf_processor.extract_medical_data(extracted_text)
    
    # Generate summary using embeddings for better context
    summary = await generate_summary_with_embeddings(extracted_text, chunks, embedding_generator)
    
    # Create document record with actual data
    document = MedicalDocument(
        document_id=str(uuid.uuid4()),
        document_type=document_type,
        upload_date=datetime.utcnow(),
        file_name=file.filename,
        file_size=file_size,
        summary=summary,
        extracted_data=medical_data,
        is_processed=True
    )
    
    # Store in MongoDB
    await mongo_client.add_medical_document(user_id, document)
    
    # Store in ChromaDB for vector search
    for i, chunk in enumerate(chunks):
        await chroma_client.add_document_embedding(
            user_id=user_id,
            document_id=f"{document.document_id}_chunk_{i}",
            text=chunk,
            metadata={
                "file_name": file.filename,
                "document_type": document_type.value,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "summary": summary,
                "test_type": medical_data.get("test_type", ""),
                "test_date": medical_data.get("test_date", "")
            }
        )
    
    return {
        "message": "Document uploaded successfully",
        "document_id": document.document_id,
        "summary": summary
    }

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

# Chat Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat_request: ChatRequest):
    """Chat with the AI agent using RAG and context"""
    # TODO: Implement RAG + Agent logic
    # - Retrieve relevant documents from ChromaDB
    # - Get user profile and pregnancy context
    # - Generate response using AI model
    # - Return response with sources and suggestions
    
    # Placeholder response
    response = ChatResponse(
        response="שלום! אני כאן כדי לעזור לך במהלך ההריון. איך אני יכול/ה לעזור לך היום?",
        sources=[],
        suggestions=["בדיקות רפואיות", "מטלות להכנה", "מעקב הריון"],
        confidence=0.8
    )
    
    return response

# Emergency Endpoints
@app.post("/users/{user_id}/emergency")
async def emergency_alert(user_id: str, emergency_type: str = "general"):
    """Send emergency alert with user pregnancy context"""
    user = await mongo_client.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    # TODO: Implement emergency notification system
    # - Contact emergency services
    # - Include pregnancy context
    # - Send location if available
    
    return {
        "message": "Emergency alert sent successfully",
        "user_id": user_id,
        "pregnancy_week": user.pregnancy_week,
        "emergency_type": emergency_type
    }

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

async def generate_summary_with_embeddings(text: str, chunks: List[str], embedding_generator: EmbeddingGenerator) -> str:
    """Generate summary using embeddings for better context understanding"""
    # Create embeddings for chunks to understand document structure
    chunk_embeddings = embedding_generator.generate_embeddings_batch(chunks)
    query_embedding = embedding_generator.generate_embedding(text)
    similar_chunks = embedding_generator.find_similar_documents(query_embedding, chunk_embeddings)
    
    # Use first few chunks for summary (avoid overwhelming the model)
    summary_chunks = [chunks[i] for i in similar_chunks]
    summary_text = "\n\n".join(summary_chunks)
    print(summary_text)

    pdf_processor = PDFProcessor()
    
    # Generate summary using the focused text
    return await pdf_processor.generate_summary(summary_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)