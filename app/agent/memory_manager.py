from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.database.mongo_client import mongo_client
from app.utils.embeddings import embeddings_generator
from app.utils.ai_model import ai_model

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.conversations_collection = mongo_client.get_collection("conversations")
        self.memories_collection = mongo_client.get_collection("memories")
        
    async def store_conversation(self, user_id: str, message: str, response: str, 
                               context: Dict[str, Any] = None) -> str:
        """Store a conversation turn in memory with AI analysis"""
        try:
            # Generate AI analysis of the conversation
            ai_analysis = await ai_model.analyze_conversation(
                user_id=user_id,
                message=message,
                response=response,
                context=context
            )
            
            conversation = {
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "message": message,
                "response": response,
                "context": context or {},
                "ai_analysis": ai_analysis,
                "type": "conversation"
            }
            
            result = self.conversations_collection.insert_one(conversation)
            logger.info(f"Stored conversation for user {user_id} with AI analysis")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            raise
    
    async def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversations for context with AI insights"""
        try:
            conversations = list(
                self.conversations_collection.find(
                    {"user_id": user_id},
                    sort=[("timestamp", -1)]
                ).limit(limit)
            )
            
            # Convert ObjectId to string and add AI insights
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
                
                # Add AI-generated insights if not present
                if "ai_insights" not in conv:
                    ai_insights = await ai_model.generate_conversation_insights(
                        user_id=user_id,
                        conversation=conv
                    )
                    conv["ai_insights"] = ai_insights
                
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []
    
    async def store_memory(self, user_id: str, memory_type: str, content: str, 
                          importance: float = 0.5, metadata: Dict = None) -> str:
        """Store a memory for the user with AI enhancement"""
        try:
            # Generate AI-enhanced content
            ai_enhanced_content = await ai_model.enhance_memory_content(
                user_id=user_id,
                memory_type=memory_type,
                content=content,
                metadata=metadata
            )
            
            memory = {
                "user_id": user_id,
                "memory_type": memory_type,
                "content": content,
                "ai_enhanced_content": ai_enhanced_content,
                "importance": importance,
                "metadata": metadata or {},
                "created_at": datetime.utcnow(),
                "last_accessed": datetime.utcnow()
            }
            
            result = self.memories_collection.insert_one(memory)
            logger.info(f"Stored AI-enhanced memory for user {user_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    async def get_relevant_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Get memories relevant to the current query using AI and embeddings"""
        try:
            # Get all memories for the user
            all_memories = list(
                self.memories_collection.find(
                    {"user_id": user_id},
                    sort=[("last_accessed", -1), ("importance", -1)]
                )
            )
            
            if not all_memories:
                return []
            
            # Generate embedding for the query
            query_embedding = await embeddings_generator._generate_single_embedding(query)
            
            # Generate embeddings for memories
            memory_embeddings = []
            for memory in all_memories:
                memory_text = f"{memory.get('content', '')} {memory.get('ai_enhanced_content', '')}"
                embedding = await embeddings_generator._generate_single_embedding(memory_text)
                memory_embeddings.append(embedding)
            
            # Find most similar memories
            similar_indices = await embeddings_generator.similarity_search(
                query_embedding, memory_embeddings, limit
            )
            
            # Return relevant memories
            relevant_memories = []
            for idx in similar_indices:
                if idx < len(all_memories):
                    memory = all_memories[idx]
                    memory["_id"] = str(memory["_id"])
                    relevant_memories.append(memory)
            
            return relevant_memories
            
        except Exception as e:
            logger.error(f"Failed to get relevant memories: {e}")
            # Fallback to simple retrieval
            memories = list(
                self.memories_collection.find(
                    {"user_id": user_id},
                    sort=[("last_accessed", -1), ("importance", -1)]
                ).limit(limit)
            )
            
            for memory in memories:
                memory["_id"] = str(memory["_id"])
            
            return memories
    
    async def update_memory_access(self, memory_id: str):
        """Update the last accessed time of a memory"""
        try:
            self.memories_collection.update_one(
                {"_id": memory_id},
                {"$set": {"last_accessed": datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Failed to update memory access: {e}")
    
    async def store_medical_memory(self, user_id: str, document_type: str, 
                                 content: str, importance: float = 0.8) -> str:
        """Store medical-related memory with AI analysis"""
        try:
            # Generate AI medical analysis
            ai_medical_analysis = await ai_model.analyze_medical_memory(
                user_id=user_id,
                document_type=document_type,
                content=content
            )
            
            return await self.store_memory(
                user_id=user_id,
                memory_type="medical",
                content=content,
                importance=importance,
                metadata={
                    "document_type": document_type,
                    "ai_medical_analysis": ai_medical_analysis
                }
            )
        except Exception as e:
            logger.error(f"Failed to store medical memory: {e}")
            raise
    
    async def store_pregnancy_memory(self, user_id: str, week: int, 
                                   content: str, importance: float = 0.7) -> str:
        """Store pregnancy-related memory with AI insights"""
        try:
            # Generate AI pregnancy insights
            ai_pregnancy_insights = await ai_model.analyze_pregnancy_memory(
                user_id=user_id,
                week=week,
                content=content
            )
            
            return await self.store_memory(
                user_id=user_id,
                memory_type="pregnancy",
                content=content,
                importance=importance,
                metadata={
                    "pregnancy_week": week,
                    "ai_pregnancy_insights": ai_pregnancy_insights
                }
            )
        except Exception as e:
            logger.error(f"Failed to store pregnancy memory: {e}")
            raise
    
    async def get_medical_memories(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get medical-related memories for a user with AI insights"""
        try:
            memories = list(
                self.memories_collection.find(
                    {"user_id": user_id, "memory_type": "medical"},
                    sort=[("last_accessed", -1), ("importance", -1)]
                ).limit(limit)
            )
            
            # Add AI insights to memories
            for memory in memories:
                memory["_id"] = str(memory["_id"])
                
                # Generate additional AI insights if needed
                if "ai_insights" not in memory:
                    ai_insights = await ai_model.generate_medical_memory_insights(
                        user_id=user_id,
                        memory=memory
                    )
                    memory["ai_insights"] = ai_insights
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get medical memories: {e}")
            return []
    
    async def get_pregnancy_memories(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get pregnancy-related memories for a user with AI insights"""
        try:
            memories = list(
                self.memories_collection.find(
                    {"user_id": user_id, "memory_type": "pregnancy"},
                    sort=[("last_accessed", -1), ("importance", -1)]
                ).limit(limit)
            )
            
            # Add AI insights to memories
            for memory in memories:
                memory["_id"] = str(memory["_id"])
                
                # Generate additional AI insights if needed
                if "ai_insights" not in memory:
                    ai_insights = await ai_model.generate_pregnancy_memory_insights(
                        user_id=user_id,
                        memory=memory
                    )
                    memory["ai_insights"] = ai_insights
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get pregnancy memories: {e}")
            return []
    
    async def generate_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate AI-powered memory summary for user"""
        try:
            # Get all memories for the user
            all_memories = list(
                self.memories_collection.find({"user_id": user_id})
            )
            
            # Generate AI summary
            ai_summary = await ai_model.generate_memory_summary(
                user_id=user_id,
                memories=all_memories
            )
            
            return {
                "user_id": user_id,
                "total_memories": len(all_memories),
                "ai_summary": ai_summary,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate memory summary: {e}")
            return {
                "user_id": user_id,
                "total_memories": 0,
                "ai_summary": "Unable to generate summary",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def analyze_conversation_turn(self, user_id: str, message: str, response: str) -> Dict[str, Any]:
        """Analyze a conversation turn"""
        try:
            # Use AI model to analyze the conversation
            analysis = await ai_model.analyze_conversation(
                user_id=user_id,
                message=message,
                response=response
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing conversation turn: {e}")
            return {
                "intent": "general",
                "sentiment": "neutral",
                "topics": ["pregnancy"],
                "action_needed": False,
                "follow_up": "continue_conversation"
            }

# Global instance
memory_manager = MemoryManager()