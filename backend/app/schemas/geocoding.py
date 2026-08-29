"""Geocoding request and response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List


class LocationSuggestion(BaseModel):
    """A single location suggestion"""
    display_name: str = Field(..., description="Full location name")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    country: Optional[str] = Field(None, description="Country name")
    state: Optional[str] = Field(None, description="State or province")
    city: Optional[str] = Field(None, description="City name")
    osm_id: Optional[str] = Field(None, description="OpenStreetMap ID")
    osm_type: Optional[str] = Field(None, description="OSM object type")
    boundingbox: Optional[List[float]] = Field(None, description="Bounding box [min_lat, max_lat, min_lon, max_lon]")


class GeocodingSearchResponse(BaseModel):
    """Response for geocoding search"""
    success: bool
    results: List[LocationSuggestion] = Field(default_factory=list)
    error: Optional[str] = None
    timestamp: str


class SelectedLocation(BaseModel):
    """A selected location with full details"""
    display_name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    boundingbox: Optional[List[float]] = None
    source: str = "nominatim"
