from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime
import uuid
import logging
from app.utils.pdf_processor import pdf_processor
from app.utils.embeddings import embeddings_generator
from app.database.chroma_client import chroma_client
from app.database.mongo_client import mongo_client
from app.agent.user_profile import user_profile_manager
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class MedicalDocumentResponse(BaseModel):
    document_id: str
    user_id: str
    doc_type: str
    upload_date: datetime
    status: str
    chunks_count: int
    message: str

@router.post("/medical-documents")
async def upload_medical_document(
    user_id: str = Form(...),
    doc_type: str = Form(...),
    document_date: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """Upload and process medical document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Validate document type
        if doc_type not in pdf_processor.supported_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Document type must be one of: {pdf_processor.supported_types}"
            )
        
        # Check if user profile exists
        user_profile = await user_profile_manager.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from PDF
        text_content = pdf_processor.extract_text_from_pdf(file_content)
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF")
        
        # Chunk the text
        chunks = pdf_processor.chunk_text(text_content)
        
        # Generate embeddings for chunks
        embeddings = await embeddings_generator.generate_embeddings(chunks)
        
        # Prepare metadata
        metadata = pdf_processor.extract_metadata(text_content, doc_type)
        metadata.update({
            "user_id": user_id,
            "upload_date": datetime.utcnow().isoformat(),
            "original_filename": file.filename,
            "document_date": document_date
        })
        
        # Store in ChromaDB
        document_id = str(uuid.uuid4())
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        chunk_metadatas = [metadata.copy() for _ in chunks]
        
        # Add chunk-specific metadata
        for i, chunk_metadata in enumerate(chunk_metadatas):
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
        
        await chroma_client.add_documents(chunks, chunk_metadatas, chunk_ids)
        
        # Store summary in MongoDB
        mongo_collection = mongo_client.get_collection("medical_documents")
        document_summary = {
            "document_id": document_id,
            "user_id": user_id,
            "doc_type": doc_type,
            "upload_date": datetime.utcnow(),
            "document_date": document_date,
            "original_filename": file.filename,
            "text_length": len(text_content),
            "chunks_count": len(chunks),
            "metadata": metadata,
            "status": "processed"
        }
        
        mongo_collection.insert_one(document_summary)
        
        # הוספה לפרופיל המשתמש
        await user_profile_manager.add_medical_document(user_id, document_summary)
        
        logger.info(f"Successfully processed document {document_id} for user {user_id}")
        
        return MedicalDocumentResponse(
            document_id=document_id,
            user_id=user_id,
            doc_type=doc_type,
            upload_date=datetime.utcnow(),
            status="processed",
            chunks_count=len(chunks),
            message="Document uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing medical document: {e}")
        raise HTTPException(status_code=500, detail="Failed to process document")

@router.get("/medical-documents/{user_id}")
async def get_user_documents(user_id: str):
    """Get all medical documents for a user"""
    try:
        # Get documents from user profile
        documents = await user_profile_manager.get_user_medical_documents(user_id)
        
        # Get document summary
        summary = await user_profile_manager.get_document_summary(user_id)
        
        return {
            "user_id": user_id,
            "documents": [doc.dict() for doc in documents],
            "summary": summary,
            "total_count": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error getting user documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get documents")

@router.get("/medical-documents/{user_id}/summary")
async def get_user_documents_summary(user_id: str):
    """Get summary of user's medical documents"""
    try:
        summary = await user_profile_manager.get_document_summary(user_id)
        return {
            "user_id": user_id,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting document summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document summary")

@router.get("/medical-documents/{user_id}/by-type/{doc_type}")
async def get_user_documents_by_type(user_id: str, doc_type: str):
    """Get user documents filtered by type"""
    try:
        documents = await user_profile_manager.get_user_medical_documents(user_id, doc_type)
        return {
            "user_id": user_id,
            "doc_type": doc_type,
            "documents": [doc.dict() for doc in documents],
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error getting documents by type: {e}")
        raise HTTPException(status_code=500, detail="Failed to get documents by type")

@router.delete("/medical-documents/{user_id}/{document_id}")
async def delete_user_document(user_id: str, document_id: str):
    """Delete a medical document from user profile"""
    try:
        success = await user_profile_manager.remove_medical_document(user_id, document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "message": "Document deleted successfully",
            "user_id": user_id,
            "document_id": document_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@router.post("/query-documents")
async def query_documents(
    user_id: str,
    query: str,
    doc_type: Optional[str] = None,
    limit: int = 5
):
    """Query medical documents using RAG"""
    try:
        # Query ChromaDB for relevant documents
        results = await chroma_client.query_documents(query, limit)
        
        # Filter by user_id and optionally by doc_type
        filtered_results = []
        for result in results:
            if result['metadata']['user_id'] == user_id:
                if doc_type is None or result['metadata']['doc_type'] == doc_type:
                    filtered_results.append(result)
        
        return {
            "query": query,
            "user_id": user_id,
            "results": filtered_results,
            "total_found": len(filtered_results)
        }
        
    except Exception as e:
        logger.error(f"Error querying documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to query documents")