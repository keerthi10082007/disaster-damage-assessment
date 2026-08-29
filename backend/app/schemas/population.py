"""Population data schemas"""

from pydantic import BaseModel, Field
from typing import Optional


class PopulationData(BaseModel):
    """Population information"""
    population: Optional[int] = Field(None, description="Population count")
    density: Optional[float] = Field(None, description="Population density per sq km")
    source: str = Field(..., description="Data source")
    coverage: str = Field(..., description="Coverage area description")
    available: bool = Field(..., description="Whether data is available")


class PopulationResponse(BaseModel):
    """Response for population query"""
    latitude: float
    longitude: float
    data: PopulationData
    message: Optional[str] = None
    timestamp: str
