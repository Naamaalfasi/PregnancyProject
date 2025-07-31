import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class ChromaDBClient:
    def __init__(self):
        self.client = None
        self.collection = None
        
    async def connect(self):
        """Connect to ChromaDB"""
        try:
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST.replace("http://", "").split(":")[0],
                port=int(settings.CHROMA_HOST.split(":")[-1].split("/")[0])
            )
            logger.info("Connected to ChromaDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise
    
    def get_or_create_collection(self, collection_name: str):
        """Get or create a collection for medical documents"""
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Medical documents embeddings"}
            )
            logger.info(f"Using collection: {collection_name}")
            return self.collection
        except Exception as e:
            logger.error(f"Failed to get/create collection: {e}")
            raise
    
    async def add_documents(self, documents: List[str], metadatas: List[Dict], ids: List[str]):
        """Add documents to ChromaDB with embeddings"""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def query_documents(self, query: str, n_results: int = 5) -> List[Dict]:
        """Query documents by similarity"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = []
            for i in range(len(results['documents'][0])):
                doc = {
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} relevant documents")
            return documents
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if ChromaDB is healthy"""
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False

# Global ChromaDB client instance
chroma_client = ChromaDBClient()