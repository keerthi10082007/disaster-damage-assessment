"""Zone analysis API routes"""

from fastapi import APIRouter, Query, Body
from app.schemas.zone import ZoneAnalysisResponse
from app.services.zones import zone_service
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/zones", tags=["zones"])


@router.post("/analyze", response_model=ZoneAnalysisResponse)
async def analyze_zones(latitude: float = Query(..., ge=-90, le=90),
                       longitude: float = Query(..., ge=-180, le=180),
                       affected_area_km2: Optional[float] = Body(None),
                       population: Optional[int] = Body(None),
                       damage_data: Optional[Dict[str, Any]] = Body(None),
                       infrastructure: Optional[List[Dict[str, Any]]] = Body(None)):
    """Analyze zones in affected area"""
    result = await zone_service.analyze_zones(
        latitude=latitude,
        longitude=longitude,
        affected_area_km2=affected_area_km2,
        population=population,
        damage_data=damage_data,
        infrastructure=infrastructure
    )
    return result
