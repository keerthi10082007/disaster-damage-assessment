"""Population API routes"""

from fastapi import APIRouter, Query
from app.schemas.population import PopulationResponse
from app.services.population import population_service

router = APIRouter(prefix="/population", tags=["population"])


@router.get("/", response_model=PopulationResponse)
async def get_population(latitude: float = Query(..., ge=-90, le=90),
                        longitude: float = Query(..., ge=-180, le=180),
                        radius_km: int = Query(10, ge=1, le=50)):
    """Get population information for a location"""
    result = await population_service.get_population(latitude, longitude, radius_km)
    return result
