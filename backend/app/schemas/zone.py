"""Zone analysis schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List


class Zone(BaseModel):
    """An analysis zone"""
    zone_id: str = Field(..., description="Zone identifier")
    location: str = Field(..., description="Zone location description")
    affected_area: Optional[float] = Field(None, description="Area in sq km")
    population: Optional[int] = Field(None, description="Population affected")
    buildings: Optional[int] = Field(None, description="Total buildings")
    damaged_buildings: Optional[int] = Field(None, description="Damaged buildings")
    roads: Optional[int] = Field(None, description="Total roads")
    road_impact: Optional[str] = Field(None, description="Road impact assessment")
    infrastructure: List[str] = Field(default_factory=list, description="Infrastructure in zone")
    severity: Optional[str] = Field(None, description="Severity level")
    accessibility: Optional[str] = Field(None, description="Accessibility status")


class ZoneAnalysisResponse(BaseModel):
    """Response for zone analysis"""
    latitude: float
    longitude: float
    zones: List[Zone] = Field(default_factory=list)
    total_zones: int
    timestamp: str
