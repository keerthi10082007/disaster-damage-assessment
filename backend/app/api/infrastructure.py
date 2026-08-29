"""Infrastructure API routes"""

from fastapi import APIRouter, Query
from app.schemas.infrastructure import InfrastructureResponse
from app.services.infrastructure import infrastructure_service

router = APIRouter(prefix="/infrastructure", tags=["infrastructure"])


@router.get("/", response_model=InfrastructureResponse)
async def get_infrastructure(latitude: float = Query(..., ge=-90, le=90),
                           longitude: float = Query(..., ge=-180, le=180),
                           radius_km: int = Query(10, ge=1, le=50)):
    """Get infrastructure near a location"""
    result = await infrastructure_service.get_nearby_infrastructure(latitude, longitude, radius_km)
    return result
