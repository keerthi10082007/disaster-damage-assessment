"""Priority calculation API routes"""

from fastapi import APIRouter, Query, Body
from app.schemas.priority import PriorityRequest, PriorityResponse
from app.services.priority import priority_service
from typing import Optional, List

router = APIRouter(prefix="/priority", tags=["priority"])


@router.post("/calculate", response_model=PriorityResponse)
async def calculate_priority(latitude: float = Query(..., ge=-90, le=90),
                           longitude: float = Query(..., ge=-180, le=180),
                           damage_severity: Optional[str] = Body(None),
                           population_exposure: Optional[int] = Body(None),
                           affected_area: Optional[float] = Body(None),
                           infrastructure_impact: Optional[List[str]] = Body(None),
                           accessibility: Optional[str] = Body(None)):
    """Calculate emergency priority"""
    result = await priority_service.calculate_priority(
        latitude=latitude,
        longitude=longitude,
        damage_severity=damage_severity,
        population_exposure=population_exposure,
        affected_area=affected_area,
        infrastructure_impact=infrastructure_impact,
        accessibility=accessibility
    )
    return result
