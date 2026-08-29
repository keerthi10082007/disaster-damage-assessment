"""Disaster events API routes"""

from fastapi import APIRouter, Query
from app.schemas.disaster import DisasterEventResponse
from app.services.disasterEvents import disaster_service
from datetime import datetime

router = APIRouter(prefix="/disasters", tags=["disasters"])


@router.get("/nearby", response_model=DisasterEventResponse)
async def get_nearby_disasters(latitude: float = Query(..., ge=-90, le=90),
                             longitude: float = Query(..., ge=-180, le=180),
                             radius_km: int = Query(100, ge=10, le=500)):
    """Get disaster events near a location"""
    try:
        result = await disaster_service.get_nearby_events(latitude, longitude, radius_km)
        return result
    except Exception as e:
        return DisasterEventResponse(
            success=False,
            status="Data Unavailable",
            events=[],
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )
