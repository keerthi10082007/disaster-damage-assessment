"""Geocoding API routes"""

from fastapi import APIRouter, Query, HTTPException
from app.schemas.geocoding import GeocodingSearchResponse, SelectedLocation
from app.services.geocoding import geocode_service
from datetime import datetime

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.get("/search", response_model=GeocodingSearchResponse)
async def search_locations(q: str = Query(..., min_length=2, max_length=255),
                          limit: int = Query(10, ge=1, le=50)):
    """Search for locations matching query"""
    try:
        result = await geocode_service.search(q, limit)
        return result
    except Exception as e:
        return GeocodingSearchResponse(
            success=False,
            results=[],
            error=str(e),
            timestamp=datetime.utcnow().isoformat()
        )


@router.get("/reverse")
async def reverse_geocode(latitude: float = Query(..., ge=-90, le=90),
                         longitude: float = Query(..., ge=-180, le=180)):
    """Reverse geocode coordinates to location name"""
    try:
        result = await geocode_service.reverse_geocode(latitude, longitude)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
