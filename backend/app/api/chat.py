"""Chatbot API routes"""

from fastapi import APIRouter, Body
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import chatbot_service
from typing import Dict, Any

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with disaster analysis bot"""
    try:
        result = await chatbot_service.answer_question(
            question=request.question,
            location_name=request.location_name,
            latitude=request.latitude,
            longitude=request.longitude,
            analysis_context=request.analysis_context
        )
        return result
    except Exception as e:
        from datetime import datetime
        return ChatResponse(
            answer=f"Chatbot error: {str(e)}",
            sources=[],
            timestamp=datetime.utcnow().isoformat()
        )
