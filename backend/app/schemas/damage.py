"""Damage assessment schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DamageAssessmentResult(BaseModel):
    """Damage assessment result"""
    affected_area: Optional[float] = Field(None, description="Affected area in square km")
    damaged_buildings: Optional[int] = Field(None, description="Number of damaged buildings")
    damaged_roads: Optional[int] = Field(None, description="Number of damaged roads")
    building_damage_categories: Optional[Dict[str, int]] = Field(None, description="Damage category counts")
    road_obstruction: Optional[int] = Field(None, description="Number of obstructed roads")
    accessibility_impact: Optional[str] = Field(None, description="Accessibility impact assessment")
    critical_infrastructure_impact: Optional[List[str]] = Field(None, description="Impacted infrastructure")
    damage_severity: Optional[str] = Field(None, description="Overall severity: Low, Medium, High, Critical")
    confidence: Optional[float] = Field(None, description="Assessment confidence")
    model: str = Field(..., description="Model used")
    model_version: str = Field(..., description="Model version")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class DamageAssessmentRequest(BaseModel):
    """Request for damage assessment"""
    current_image_url: str = Field(..., description="Current satellite image URL")
    historical_image_url: Optional[str] = Field(None, description="Historical image URL")
    latitude: float = Field(..., description="Location latitude")
    longitude: float = Field(..., description="Location longitude")
    disaster_type: str = Field(..., description="Type of disaster")
    detection_result: Optional[Dict[str, Any]] = Field(None, description="Detection result if available")


class DamageAssessmentResponse(BaseModel):
    """Response for damage assessment"""
    available: bool
    result: Optional[DamageAssessmentResult] = None
    message: Optional[str] = Field(None, description="Error or status message")
    timestamp: str
