"""Chatbot schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatMessage(BaseModel):
    """A chat message"""
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chatbot"""
    question: str = Field(..., description="User question")
    latitude: float
    longitude: float
    location_name: str
    analysis_context: Dict[str, Any] = Field(..., description="Current analysis context")


class ChatResponse(BaseModel):
    """Response from chatbot"""
    answer: str
    sources: Optional[List[str]] = None
    timestamp: str
