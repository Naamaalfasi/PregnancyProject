from typing import Optional, List
from datetime import datetime
import uuid
from app.database.mongo_client import MongoDBClient
from app.models.chat import Conversation, ChatMessage
from app.models.user import UserProfile
from app.agent.chatAI import chain
from app.config import settings
import google.generativeai as genai
from fastapi import HTTPException


class ChatService:
    def __init__(self, mongo_client: MongoDBClient):
        self.mongo_client = mongo_client
        self.token_limit = 4000
        self.warning_threshold = 3200  # 80% of limit
        
        # Configure Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self._gemini = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def should_archive_conversation(self, conversation: Conversation, new_message: str) -> bool:
        """Check if conversation should be archived after adding new message"""
        current_tokens =  len(str((await self.get_conversation_context(conversation)))) // 4
        new_message_tokens = len(new_message) // 4
        
        # If current + new message exceeds 80% of limit (3200), archive after this exchange
        return (current_tokens + new_message_tokens) >= self.warning_threshold
    
    async def generate_subject(self, first_message: str) -> str:
        """Generate conversation subject from first message"""
        # First 30 characters or 6 words, whichever is shorter
        if len(first_message) <= 30:
            return first_message
        
        words = first_message.split()
        if len(words) <= 6:
            return first_message
        
        return " ".join(words[:6])
    
    async def create_new_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation and set as active"""
        conversation_id = str(uuid.uuid4())
        
        conversation = Conversation(
            conversation_id=conversation_id,
            subject="New Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            messages=[]
        )
        
        await self.mongo_client.create_conversation(user_id, conversation)
        
        return conversation
    
    async def add_message_to_conversation(self, user_id: str, conversation_id: str, role: str, content: str):
        """Add a message to a conversation"""
        message = ChatMessage(
            message_id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )

        conversation = await self.mongo_client.get_conversation(user_id, conversation_id)
        if conversation.subject == "New Conversation":
            subject = await self.generate_subject(content)
            await self.mongo_client.update_one(user_id, "updated_at", datetime.utcnow())
            await self.mongo_client.update_one(user_id, "subject", subject) 

        await self.mongo_client.add_message_to_conversation(user_id, conversation_id, message)
        return True
    
    async def get_conversation_context(self, conversation: Conversation) -> str:
        """Get conversation context"""
        context = ""
        for message in conversation.messages:
            context += f"{message.role}: {message.content}\n"
        return context
    
    async def generate_ai_response(self, user: UserProfile, user_message: str) -> str:
        """Generate AI response using chatAI module"""
        # Build context from conversation
        conversation = await self.mongo_client.get_active_conversation(user.user_id)
        context = await self.get_conversation_context(conversation)
        
        filtered_user = user.dict(exclude={'conversations'})
        # Prepare payload for chatAI module
        payload = {
            "UserProfile": filtered_user,
            "context": context,
            "question": user_message
        }
        
        try:
            # Use the chatAI module
            answer = chain.invoke(payload)
            return answer
        except Exception as e:
            # Fallback to direct Gemini call if chatAI fails
            prompt_profile = filtered_user
            
            prompt = f"""
                Answer the question below.

                USER PROFILE: {prompt_profile}

                HERE is the conversation history: {context}

                Question: {user_message}

                IMPORTANT:
                - Use the UserProfile ONLY to personalize the answer.
                - Consider the user's pregnancy week, medical conditions, and allergies
                - Provide safe, evidence-based pregnancy advice
                - If medical concerns arise, suggest consulting a healthcare provider
                - Be supportive and informative
                - If the private context is missing or not relevant, answer from your general medical knowledge.

                Your answer:
                """.strip()
            
            resp = self._gemini.generate_content(prompt)
            return resp.text if hasattr(resp, "text") else str(resp)
    
    async def process_chat_message(self, user_id: str, message: str) -> dict:
        """Main method to process a chat message"""
        # Get user profile
        user = await self.mongo_client.get_user_profile(user_id)
        if not user:
            return False
        
        # Get or create active conversation
        active_conversation = await self.mongo_client.get_active_conversation(user_id)
        if not active_conversation:
            active_conversation = await self.create_new_conversation(user_id)
        
        # Check if we should archive after this exchange
        should_archive = await self.should_archive_conversation(active_conversation, message)
        
        # Add user message
        await self.add_message_to_conversation(
            user_id, 
            active_conversation.conversation_id, 
            "user", 
            message
        )
        
        # Generate AI response
        try:
            ai_response = await self.generate_ai_response(user, message)
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "ResourceExhausted" in err_msg:
                raise HTTPException(status_code=429, detail="Gemini quota exceeded. Please try again later.")
            raise HTTPException(status_code=500, detail="Gemini error: " + err_msg)
        
        # Add AI response
        await self.add_message_to_conversation(
            user_id, 
            active_conversation.conversation_id, 
            "ai", 
            ai_response
        )
        
        # Archive conversation if needed
        if should_archive:
            await self.create_new_conversation(user_id)
            return {
                "response": ai_response, 
                "conversation_archived": True,
                "conversation_id": active_conversation.conversation_id
            }
        
        return {
            "response": ai_response, 
            "conversation_archived": False,
            "conversation_id": active_conversation.conversation_id
        }

    async def switch_to_conversation(self, user_id: str, conversation_id: str) -> Conversation:
        """Switch to a specific conversation"""
        conversation = await self.mongo_client.get_conversation(user_id, conversation_id)
        await self.mongo_client.set_active_conversation(user_id, conversation_id)
        return conversation

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user"""
        conversations = await self.mongo_client.get_user_conversations(user_id)
        if not conversations:
            return []
        return conversations
    
    async def get_conversation_by_id(self, user_id: str, conversation_id: str) -> Optional[Conversation]:
        """Get specific conversation by ID"""
        conversation = await self.mongo_client.get_conversation(user_id, conversation_id)
        if not conversation:
            return None
        return conversation
