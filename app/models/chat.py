from pydantic import BaseModel
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