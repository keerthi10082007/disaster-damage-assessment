"""Infrastructure data schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List


class InfrastructureFeature(BaseModel):
    """A single infrastructure feature"""
    name: str = Field(..., description="Feature name")
    feature_type: str = Field(..., description="Type: Hospital, School, Bridge, etc")
    latitude: float = Field(..., description="Feature latitude")
    longitude: float = Field(..., description="Feature longitude")
    distance_km: float = Field(..., description="Distance from center in km")
    source: str = Field(..., description="Data source")
    osm_id: Optional[str] = Field(None, description="OpenStreetMap ID")


class InfrastructureResponse(BaseModel):
    """Response for infrastructure query"""
    latitude: float
    longitude: float
    radius_km: int
    features: List[InfrastructureFeature] = Field(default_factory=list)
    total_count: int
    available: bool
    message: Optional[str] = None
    timestamp: str
