"""Emergency priority schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PriorityFactor(BaseModel):
    """A factor contributing to priority score"""
    name: str = Field(..., description="Factor name")
    value: Any = Field(..., description="Factor value")
    weight: float = Field(..., description="Factor weight in calculation")
    contribution: float = Field(..., description="Contribution to overall score")


class PriorityResult(BaseModel):
    """Emergency priority result"""
    score: float = Field(..., description="Priority score (0-100)")
    level: str = Field(..., description="Priority level: HIGH, MEDIUM, LOW")
    factors_used: List[PriorityFactor] = Field(default_factory=list)
    unavailable_factors: List[str] = Field(default_factory=list)
    reason: str = Field(..., description="Explanation of priority")


class PriorityRequest(BaseModel):
    """Request for priority calculation"""
    latitude: float
    longitude: float
    damage_severity: Optional[str] = None
    population_exposure: Optional[int] = None
    affected_area: Optional[float] = None
    infrastructure_impact: Optional[List[str]] = None
    accessibility: Optional[str] = None


class PriorityResponse(BaseModel):
    """Response for priority calculation"""
    result: PriorityResult
    timestamp: str
