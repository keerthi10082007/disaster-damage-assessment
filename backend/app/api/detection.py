"""Image detection API routes"""

from fastapi import APIRouter, HTTPException
from app.schemas.detection import ImageDetectionRequest, ImageDetectionResponse
from app.services.imageDetector import image_detector
from datetime import datetime

router = APIRouter(prefix="/detection", tags=["detection"])


@router.post("/analyze", response_model=ImageDetectionResponse)
async def analyze_image(request: ImageDetectionRequest):
    """Analyze satellite image for disaster detection"""
    try:
        result = await image_detector.analyze_image(
            image_url=request.image_url,
            latitude=request.latitude,
            longitude=request.longitude,
            disaster_type=request.disaster_type,
            source=request.source,
            acquisition_date=request.acquisition_date
        )
        return result
    except Exception as e:
        return ImageDetectionResponse(
            available=False,
            message=str(e),
            timestamp=datetime.utcnow().isoformat()
        )
