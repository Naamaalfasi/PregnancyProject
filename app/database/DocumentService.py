from typing import List
from app.models import UserProfile, MedicalDocument, Task, ChatRequest, ChatResponse, DocumentType
from app.database.mongo_client import MongoDBClient
from app.database.chroma_client import ChromaDBClient
from app.utils.pdf_processor import PDFProcessor
from app.utils.embeddings import EmbeddingGenerator
from app.agent.medical_processor import MedicalDataProcessor
from app.database.file_storage import FileStorageService
from app.database.file_processing import DocumentStatus
from fastapi import UploadFile, File
from typing import List
import uuid
from datetime import datetime
import os

class DocumentService:
    def __init__(self, mongo_client: MongoDBClient, chroma_client: ChromaDBClient, pdf_processor: PDFProcessor, embedding_generator: EmbeddingGenerator, medical_processor: MedicalDataProcessor, file_storage: FileStorageService):
        self.mongo_client = mongo_client
        self.chroma_client = chroma_client
        self.pdf_processor = pdf_processor
        self.embedding_generator = embedding_generator
        self.medical_processor = medical_processor
        self.file_storage = file_storage
    
    async def generate_summary_with_embeddings(self, text: str, chunks: List[str]) -> str:
        """Generate summary using embeddings for better context understanding"""
        # Create embeddings for chunks to understand document structure
        chunk_embeddings = self.embedding_generator.generate_embeddings_batch(chunks)
        text_embedding = self.embedding_generator.generate_embedding(text)
        similar_chunks = self.embedding_generator.find_similar_documents(text_embedding, chunk_embeddings)

        # Use first few chunks for summary (avoid overwhelming the model)
        summary_chunks = [chunks[i] for i in similar_chunks]
        summary_text = "\n\n".join(summary_chunks)
        print(summary_text)
        # Generate summary using the focused text
        return await self.medical_processor.generate_summary(summary_text)

    async def create_document(self, user_id: str, file: UploadFile, document_type: DocumentType = DocumentType.OTHER): 
        """Create and upload a medical document"""
        file_path = await self.file_storage.save_uploaded_file(user_id, file)

        document = MedicalDocument(
            document_id=str(uuid.uuid4()),
            document_type=document_type,
            upload_date=datetime.utcnow(),
            file_name=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            status=DocumentStatus.UPLOADED,
            summary="Not processed yet"
        )

        await self.mongo_client.add_medical_document(user_id, document, {})

        return {
            "message": "Document uploaded successfully",
            "document_id": document.document_id,
            "status": document.status,
            "summary": document.summary,
            "path": document.file_path
        }

    async def process_document(self, user_id: str, document_id: str):
        """Process a document in the background"""
        document = await self.mongo_client.get_medical_document(user_id, document_id)

        # Read file content
        file_content = self.file_storage.read_file_as_bytes(document.file_path)

        # Extract text and process document
        extracted_text = self.pdf_processor.extract_text_from_pdf(file_content)
        chunks = self.pdf_processor.chunk_text(extracted_text)
        medical_data = await self.medical_processor.extract_medical_data(extracted_text)
        summary = await self.generate_summary_with_embeddings(extracted_text, chunks)
        parsed_medical_data = self.pdf_processor.parse_medical_summary(medical_data)

        # Update document with extracted data
        await self.mongo_client.update_document_with_medical_data(user_id, document_id, parsed_medical_data, summary)

        # Store in ChromaDB for vector search
        for i, chunk in enumerate(chunks):
            await self.chroma_client.add_document_embedding(
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
        
        return {
            "message": "Document processed successfully",
            "document_id": document.document_id,
            "summary": summary,
            "before_extraction": medical_data,
            "extracted_medical_data": parsed_medical_data
        }

    async def document_upload_and_process(self, user_id: str, file: UploadFile = File(...), document_type: DocumentType = DocumentType.OTHER):
        # First create the document
            result = await self.create_document(user_id, file, document_type)
            document_id = result["document_id"]
            
            # Then process it
            process_result = await self.process_document(user_id, document_id)
            
            await self.mongo_client.update_document_status(user_id, document_id, DocumentStatus.COMPLETED)

            return {
                "upload_result": result,
                "process_result": process_result
            }


