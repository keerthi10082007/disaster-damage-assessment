"""Damage assessment API routes"""

from fastapi import APIRouter
from app.schemas.damage import DamageAssessmentRequest, DamageAssessmentResponse
from app.services.damageAssessment import damage_service
from datetime import datetime

router = APIRouter(prefix="/damage", tags=["damage"])


@router.post("/analyze", response_model=DamageAssessmentResponse)
async def analyze_damage(request: DamageAssessmentRequest):
    """Analyze damage from satellite imagery"""
    try:
        result = await damage_service.analyze_damage(
            current_image_url=request.current_image_url,
            historical_image_url=request.historical_image_url,
            latitude=request.latitude,
            longitude=request.longitude,
            disaster_type=request.disaster_type,
            detection_result=request.detection_result
        )
        return result
    except Exception as e:
        return DamageAssessmentResponse(
            available=False,
            message=str(e),
            timestamp=datetime.utcnow().isoformat()
        )
