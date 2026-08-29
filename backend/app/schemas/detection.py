"""Image detection schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BoundingBox(BaseModel):
    """Object detection bounding box"""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., description="Box width")
    height: float = Field(..., description="Box height")
    class_name: str = Field(..., description="Detected class")
    confidence: float = Field(..., description="Detection confidence")


class DetectionResult(BaseModel):
    """Image detection result"""
    disaster_detected: bool
    disaster_type: Optional[str] = Field(None, description="Type of disaster detected")
    confidence: Optional[float] = Field(None, description="Overall confidence")
    detections: List[BoundingBox] = Field(default_factory=list)
    segmentation_masks: Optional[List[Dict[str, Any]]] = Field(None, description="Segmentation masks if available")
    model: str = Field(..., description="Model used")
    model_version: str = Field(..., description="Model version")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class ImageDetectionRequest(BaseModel):
    """Request for image detection"""
    image_url: str = Field(..., description="URL to image")
    latitude: float = Field(..., description="Image latitude")
    longitude: float = Field(..., description="Image longitude")
    disaster_type: Optional[str] = Field(None, description="Expected disaster type")
    source: str = Field(..., description="Image source")
    acquisition_date: str = Field(..., description="Image acquisition date")


class ImageDetectionResponse(BaseModel):
    """Response for image detection"""
    available: bool
    result: Optional[DetectionResult] = None
    message: Optional[str] = Field(None, description="Error or status message")
    timestamp: str
