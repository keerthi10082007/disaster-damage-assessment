"""AI assistance schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis"""
    latitude: float
    longitude: float
    location_name: str
    disaster_type: Optional[str] = None
    analysis_data: Dict[str, Any] = Field(..., description="Analysis data from various services")


class AIAnalysisResponse(BaseModel):
    """Response for AI analysis"""
    situation_summary: str
    detected_disaster: str
    damage_summary: str
    change_analysis: str
    priority_explanation: str
    recommended_response: str
    data_sources: list
    data_limitations: list
    timestamp: str
