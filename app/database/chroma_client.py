import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid

from app.config import settings

class ChromaDBClient:
    def __init__(self):
        self.client = None
        self.collection = None
        
    async def connect(self):
        """Connect to ChromaDB"""
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST.replace("http://", "").split(":")[0],
            port=int(settings.CHROMA_HOST.split(":")[-1])
        )
        
        # Create or get collection for medical documents
        self.collection = self.client.get_or_create_collection(
            name="medical_documents",
            metadata={"description": "Medical documents embeddings"}
        )
        
    async def close(self):
        """Close ChromaDB connection"""
        if self.client:
            self.client.close()
            
    async def add_document_embedding(
        self, 
        user_id: str,  # ✅ הוספנו user_id!
        document_id: str, 
        text: str, 
        metadata: Dict[str, Any]
    ):
        """Add document embedding to ChromaDB"""
        # TODO: Generate embedding using language model
        # For now, we'll use a placeholder embedding
        embedding = [0.0] * 384  # Placeholder embedding vector
        
        # ✅ הוספת user_id לmetadata
        metadata_with_user = {
            **metadata,
            "user_id": user_id,  # �� זה מבדיל בין משתמשים!
            "document_id": document_id
        }
        
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata_with_user],
            ids=[document_id]
        )
        
    async def search_documents(
        self, 
        user_id: str,  # ✅ הוספנו user_id!
        query: str, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents - ONLY for specific user"""
        # TODO: Generate query embedding
        # For now, we'll use a placeholder embedding
        query_embedding = [0.0] * 384
        
        # ✅ חיפוש רק במסמכים של המשתמש הספציפי
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"user_id": user_id}  # 🔒 פילטר לפי user_id!
        )
        
        return results
        
    async def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a specific user"""
        # ✅ קבלת כל המסמכים של משתמש ספציפי
        results = self.collection.get(
            where={"user_id": user_id}
        )
        
        return results
        
    async def delete_user_document(self, user_id: str, document_id: str):
        """Delete a specific document for a user"""
        # ✅ מחיקת מסמך ספציפי של משתמש
        self.collection.delete(
            ids=[document_id],
            where={"user_id": user_id}
        )