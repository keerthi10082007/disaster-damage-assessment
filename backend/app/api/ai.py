"""AI analysis API routes"""

from fastapi import APIRouter, Body
from app.schemas.ai import AIAnalysisRequest, AIAnalysisResponse
from app.services.gemini import gemini_service
from typing import Dict, Any

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_disaster(request: AIAnalysisRequest):
    """Get AI-powered analysis of disaster"""
    try:
        result = await gemini_service.analyze_disaster(
            location_name=request.location_name,
            latitude=request.latitude,
            longitude=request.longitude,
            analysis_data=request.analysis_data
        )
        return result
    except Exception as e:
        from datetime import datetime
        return AIAnalysisResponse(
            situation_summary="AI analysis error",
            detected_disaster="Unknown",
            damage_summary=str(e),
            change_analysis="N/A",
            priority_explanation="N/A",
            recommended_response="Please try again",
            data_sources=[],
            data_limitations=["AI service error"],
            timestamp=datetime.utcnow().isoformat()
        )
