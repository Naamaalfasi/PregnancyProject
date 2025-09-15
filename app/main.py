from fastapi import FastAPI, HTTPException, UploadFile, File, APIRouter, Body
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
import os
from app.models.tasks import TaskCreate, TaskUpdate
from pydantic import BaseModel
import google.generativeai as genai
from datetime import date, timedelta
from app.agent.task_manager import TaskManager

# Initialize database clients
mongo_client = MongoDBClient()
chroma_client = ChromaDBClient()

task_manager = TaskManager(
    mongo_client=mongo_client
    
)

file_storage = FileStorageService()


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

    file_path = await file_storage.save_uploaded_file(user_id, file)

    document = MedicalDocument(
        document_id=str(uuid.uuid4()),
        document_type=document_type,
        upload_date=datetime.utcnow(),
        file_name=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        status=DocumentStatus.UPLOADED,
        summary= "Not processed yet"
    )

    # Store in MongoDB
    await mongo_client.add_medical_document(user_id, document, {})

    return {"message": "Document uploaded successfully",
            "document_id": document.document_id,
            "status": document.status,
            "summary": document.summary,
            "path": document.file_path
            }
    
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

    pdf_processor = PDFProcessor()
    embedding_generator = EmbeddingGenerator()
    medical_processor = MedicalDataProcessor()

    # Read file content
    file_content = file_storage.read_file_as_bytes(document.file_path)

    # Extract text and process document
    extracted_text = pdf_processor.extract_text_from_pdf(file_content)
    chunks = pdf_processor.chunk_text(extracted_text)
    medical_data = await medical_processor.extract_medical_data(extracted_text)
    summary = await generate_summary_with_embeddings(extracted_text, chunks, embedding_generator)
    parsed_medical_data = pdf_processor.parse_medical_summary(medical_data)

    await mongo_client.update_document_with_medical_data(user_id, document_id, parsed_medical_data, summary)

    # Store in ChromaDB for vector search
    for i, chunk in enumerate(chunks):
        await chroma_client.add_document_embedding(
            user_id=user_id,
            document_id=f"{document.document_id}_chunk_{i}",
            text=chunk,
            metadata={
                "file_name": document.file_name,
                "document_type": document.document_type.value,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "summary": summary,
                "test_type": parsed_medical_data.get("test_type", ""),
                "test_date": parsed_medical_data.get("test_date", "")
            }
        )
    
    await mongo_client.update_document_status(user_id, document_id, DocumentStatus.COMPLETED)
    
    return {
        "message": "Document processed successfully",
        "document_id": document.document_id,
        "summary": summary,
        "before_extraction": medical_data,
        "extracted_medical_data": parsed_medical_data
    }


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

async def generate_summary_with_embeddings(text: str, chunks: List[str], embedding_generator: EmbeddingGenerator) -> str:
    """Generate summary using embeddings for better context understanding"""
    # Create embeddings for chunks to understand document structure
    chunk_embeddings = embedding_generator.generate_embeddings_batch(chunks)
    text_embedding = embedding_generator.generate_embedding(text)
    similar_chunks = embedding_generator.find_similar_documents(text_embedding, chunk_embeddings)
    
    # Use first few chunks for summary (avoid overwhelming the model)
    summary_chunks = [chunks[i] for i in similar_chunks]
    summary_text = "\n\n".join(summary_chunks)
    print(summary_text)

    medical_processor = MedicalDataProcessor()
    
    # Generate summary using the focused text
    return await medical_processor.generate_summary(summary_text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
