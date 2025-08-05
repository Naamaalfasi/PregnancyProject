import requests
import json
import logging
from typing import List, Dict, Any
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingsGenerator:
    def __init__(self, ollama_host: str = None):
        self.ollama_host = ollama_host or settings.OLLAMA_HOST
        self.model_name = "llama2"  # Default model for embeddings
        
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Ollama"""
        embeddings = []
        
        for text in texts:
            try:
                embedding = await self._generate_single_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to generate embedding for text: {e}")
                # Return zero vector as fallback
                embeddings.append([0.0] * 384)  # Default dimension
                
        return embeddings
    
    async def _generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            url = f"{self.ollama_host}/api/embeddings"
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            embedding = result.get("embedding", [])
            
            if not embedding:
                raise ValueError("No embedding returned from Ollama")
                
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def similarity_search(self, query_embedding: List[float], 
                              document_embeddings: List[List[float]], 
                              top_k: int = 5) -> List[int]:
        """Find most similar documents using cosine similarity"""
        if not document_embeddings:
            return []
            
        similarities = []
        for doc_embedding in document_embeddings:
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append(similarity)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return top_indices.tolist()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return dot_product / (norm1 * norm2)
    
    async def generate_context_embedding(self, context: Dict[str, Any]) -> List[float]:
        """Generate embedding for conversation context"""
        try:
            # Convert context to text representation
            context_text = self._context_to_text(context)
            return await self._generate_single_embedding(context_text)
        except Exception as e:
            logger.error(f"Error generating context embedding: {e}")
            return [0.0] * 384
    
    def _context_to_text(self, context: Dict[str, Any]) -> str:
        """Convert context dictionary to text representation"""
        text_parts = []
        
        if "user_profile" in context and context["user_profile"]:
            profile = context["user_profile"]
            text_parts.append(f"User: {profile.get('name', 'Unknown')}")
            if profile.get('pregnancy_week'):
                text_parts.append(f"Pregnancy week: {profile['pregnancy_week']}")
        
        if "medical_documents" in context:
            docs = context["medical_documents"]
            if docs:
                doc_types = [doc.get('doc_type', 'unknown') for doc in docs]
                text_parts.append(f"Medical documents: {', '.join(doc_types)}")
        
        if "recent_conversations" in context:
            conversations = context["recent_conversations"]
            if conversations:
                recent_messages = [conv.get('message', '') for conv in conversations[:3]]
                text_parts.append(f"Recent conversations: {' '.join(recent_messages)}")
        
        return " | ".join(text_parts)
    
    async def find_similar_contexts(self, query_context: Dict[str, Any], 
                                  stored_contexts: List[Dict[str, Any]], 
                                  top_k: int = 3) -> List[Dict[str, Any]]:
        """Find similar contexts using embeddings"""
        try:
            # Generate embedding for query context
            query_embedding = await self.generate_context_embedding(query_context)
            
            # Generate embeddings for stored contexts
            stored_embeddings = []
            for context in stored_contexts:
                embedding = await self.generate_context_embedding(context)
                stored_embeddings.append(embedding)
            
            # Find similar contexts
            similar_indices = await self.similarity_search(query_embedding, stored_embeddings, top_k)
            
            # Return similar contexts
            similar_contexts = []
            for idx in similar_indices:
                if idx < len(stored_contexts):
                    similar_contexts.append(stored_contexts[idx])
            
            return similar_contexts
            
        except Exception as e:
            logger.error(f"Error finding similar contexts: {e}")
            return []

# Global instance
embeddings_generator = EmbeddingsGenerator()