"""Disaster event schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DisasterEvent(BaseModel):
    """A disaster event"""
    id: str = Field(..., description="Event ID")
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    event_type: str = Field(..., description="Type of event (Flood, Wildfire, etc)")
    latitude: float = Field(..., description="Event latitude")
    longitude: float = Field(..., description="Event longitude")
    date: datetime = Field(..., description="Event date")
    source: str = Field(..., description="Event source (NASA, etc)")
    distance_km: Optional[float] = Field(None, description="Distance from query location in km")


class DisasterEventResponse(BaseModel):
    """Response for disaster events query"""
    success: bool
    status: str = Field(..., description="Event status: 'Active Event', 'No Active Event', 'Data Unavailable'")
    events: List[DisasterEvent] = Field(default_factory=list)
    latitude: float
    longitude: float
    radius_km: int
    error: Optional[str] = None
    timestamp: str
