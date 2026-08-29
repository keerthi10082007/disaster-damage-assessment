"""Satellite imagery API routes"""

from fastapi import APIRouter, Query
from app.schemas.imagery import SatelliteImageResponse
from app.services.imagery import imagery_service
from datetime import datetime

router = APIRouter(prefix="/imagery", tags=["imagery"])


@router.get("/current", response_model=SatelliteImageResponse)
async def get_current_imagery(latitude: float = Query(..., ge=-90, le=90),
                            longitude: float = Query(..., ge=-180, le=180),
                            days_back: int = Query(30, ge=1, le=365)):
    """Get current satellite imagery"""
    try:
        result = await imagery_service.get_current_imagery(latitude, longitude, days_back)
        return result
    except Exception as e:
        return SatelliteImageResponse(
            available=False,
            message=str(e),
            timestamp=datetime.utcnow().isoformat()
        )


@router.get("/historical", response_model=SatelliteImageResponse)
async def get_historical_imagery(latitude: float = Query(..., ge=-90, le=90),
                               longitude: float = Query(..., ge=-180, le=180),
                               year: int = Query(..., ge=2015, le=2026),
                               month: int = Query(6, ge=1, le=12)):
    """Get historical satellite imagery"""
    try:
        result = await imagery_service.get_historical_imagery(latitude, longitude, year, month)
        return result
    except Exception as e:
        return SatelliteImageResponse(
            available=False,
            message=str(e),
            timestamp=datetime.utcnow().isoformat()
        )
