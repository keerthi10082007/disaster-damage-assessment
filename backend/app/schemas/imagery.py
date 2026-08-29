"""Satellite imagery schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ImageMetadata(BaseModel):
    """Metadata for a satellite image"""
    acquisition_date: datetime = Field(..., description="Image acquisition date")
    source: str = Field(..., description="Image source (Sentinel-2, etc)")
    sensor: str = Field(..., description="Sensor type")
    collection: Optional[str] = Field(None, description="Collection/dataset")
    cloud_coverage: Optional[float] = Field(None, description="Cloud coverage percentage")
    resolution: Optional[float] = Field(None, description="Spatial resolution in meters")
    latitude: float = Field(..., description="Center latitude")
    longitude: float = Field(..., description="Center longitude")
    bounding_box: Optional[List[float]] = Field(None, description="[min_lat, max_lat, min_lon, max_lon]")
    tile_id: Optional[str] = Field(None, description="Sentinel-2 tile ID")
    data_coverage: Optional[float] = Field(None, description="Data coverage percentage")


class SatelliteImageResponse(BaseModel):
    """Response for satellite image request"""
    available: bool
    image_url: Optional[str] = Field(None, description="URL to image (if base64 encoded in data)")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    metadata: Optional[ImageMetadata] = None
    message: Optional[str] = Field(None, description="Message if unavailable")
    timestamp: str
