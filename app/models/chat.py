from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    suggestions: List[str] = []
    confidence: float = 0.0 

class ChatMessage(BaseModel):
    message_id: str
    role: str  # "user" or "ai"
    content: str
    timestamp: datetime

class Conversation(BaseModel):
    conversation_id: str
    subject: str  # First message or user-defined subject
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []
