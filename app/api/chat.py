from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel
from app.agent.chat_router import chat_router
from app.agent.user_profile import user_profile_manager
from app.agent.memory_manager import memory_manager
from app.agent.action_planner import action_planner

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    actions: list
    context: Dict[str, Any]
    user_profile: Optional[Dict[str, Any]] = None
    needs_profile: bool = False

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    """Main chat endpoint for the pregnancy agent"""
    try:
        logger.info(f"Processing chat request for user {request.user_id}")
        
        # Process the message through the chat router
        result = await chat_router.process_message(
            user_id=request.user_id,
            message=request.message,
            context=request.context
        )
        
        return ChatResponse(
            response=result.get("response", "אני מצטערת, לא הצלחתי לעבד את ההודעה שלך."),
            actions=result.get("actions", []),
            context=result.get("context", {}),
            user_profile=result.get("user_profile"),
            needs_profile=result.get("needs_profile", False)
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 10):
    """Get chat history for a user"""
    try:
        conversations = await memory_manager.get_recent_conversations(user_id, limit)
        return {
            "user_id": user_id,
            "conversations": conversations,
            "total_count": len(conversations)
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/chat/analyze")
async def analyze_conversation(user_id: str, message: str, response: str):
    """Analyze a conversation turn"""
    try:
        analysis = await memory_manager.analyze_conversation_turn(
            user_id=user_id,
            message=message,
            response=response
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/memory-summary/{user_id}")
async def get_memory_summary(user_id: str):
    """Get AI-generated memory summary for user"""
    try:
        summary = await memory_manager.generate_memory_summary(user_id)
        return summary
    except Exception as e:
        logger.error(f"Error generating memory summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
