"""Image detection service adapter"""

import httpx
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.detection import DetectionResult, BoundingBox, ImageDetectionResponse
from app.utils.errors import DetectionError
import os
import json


class ImageDetectorService:
    """Service for image detection using configured provider"""
    
    def __init__(self):
        self.provider = os.getenv("IMAGE_DETECTOR_PROVIDER", "none").lower()
        self.api_url = os.getenv("IMAGE_DETECTOR_API_URL")
        self.api_key = os.getenv("IMAGE_DETECTOR_API_KEY")
        self.model = os.getenv("IMAGE_DETECTOR_MODEL")
        self.version = os.getenv("IMAGE_DETECTOR_VERSION", "1")
        self.timeout = 120
    
    async def analyze_image(self, image_url: str, latitude: float, longitude: float,
                           disaster_type: Optional[str] = None, source: str = "",
                           acquisition_date: str = "") -> ImageDetectionResponse:
        """Analyze satellite image for disaster detection"""
        
        # Check if detector is configured
        if self.provider == "none" or not self.api_url or not self.api_key:
            return ImageDetectionResponse(
                available=False,
                message="Image detection model is not configured.",
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            if self.provider == "roboflow":
                return await self._detect_roboflow(image_url, disaster_type)
            elif self.provider == "custom":
                return await self._detect_custom(image_url, disaster_type)
            else:
                return ImageDetectionResponse(
                    available=False,
                    message=f"Unknown detection provider: {self.provider}",
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            return ImageDetectionResponse(
                available=False,
                message=f"Image detection service unavailable: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _detect_roboflow(self, image_url: str, disaster_type: Optional[str]) -> ImageDetectionResponse:
        """Detect using Roboflow API"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Download image
                img_response = await client.get(image_url)
                img_response.raise_for_status()
                image_data = base64.b64encode(img_response.content).decode()
                
                # Send to Roboflow
                payload = {
                    "api_key": self.api_key,
                    "image": image_data
                }
                
                response = await client.post(
                    f"{self.api_url}/object-detection/{self.model}/{self.version}",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse Roboflow output
                detections = []
                disaster_detected = False
                confidence = 0.0
                
                if result.get("predictions"):
                    disaster_keywords = ["damage", "debris", "destruction", "rubble", "affected", "collapsed"]
                    
                    for pred in result["predictions"]:
                        class_name = pred.get("class", "unknown")
                        conf = pred.get("confidence", 0.0)
                        
                        # Check if this is a disaster-related detection
                        if any(keyword in class_name.lower() for keyword in disaster_keywords):
                            disaster_detected = True
                            confidence = max(confidence, conf)
                        
                        bbox = BoundingBox(
                            x=pred.get("x", 0),
                            y=pred.get("y", 0),
                            width=pred.get("width", 0),
                            height=pred.get("height", 0),
                            class_name=class_name,
                            confidence=conf
                        )
                        detections.append(bbox)
                
                detection_result = DetectionResult(
                    disaster_detected=disaster_detected,
                    disaster_type=disaster_type or ("General Damage" if disaster_detected else "No Damage"),
                    confidence=confidence if disaster_detected else None,
                    detections=detections,
                    model="Roboflow",
                    model_version=self.version,
                    processing_time_ms=result.get("inference_id", 0)
                )
                
                return ImageDetectionResponse(
                    available=True,
                    result=detection_result,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            raise DetectionError(f"Roboflow detection failed: {str(e)}")
    
    async def _detect_custom(self, image_url: str, disaster_type: Optional[str]) -> ImageDetectionResponse:
        """Detect using custom hosted model"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Download image
                img_response = await client.get(image_url)
                img_response.raise_for_status()
                
                # Send to custom endpoint
                files = {"image": img_response.content}
                payload = {"model": self.model, "disaster_type": disaster_type or "unknown"}
                
                response = await client.post(
                    self.api_url,
                    files=files,
                    data=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse custom model output
                detections = []
                for detection in result.get("detections", []):
                    bbox = BoundingBox(
                        x=detection.get("x"),
                        y=detection.get("y"),
                        width=detection.get("width"),
                        height=detection.get("height"),
                        class_name=detection.get("class"),
                        confidence=detection.get("confidence")
                    )
                    detections.append(bbox)
                
                detection_result = DetectionResult(
                    disaster_detected=result.get("disaster_detected", False),
                    disaster_type=result.get("disaster_type", disaster_type),
                    confidence=result.get("confidence"),
                    detections=detections,
                    model=result.get("model", self.model),
                    model_version=result.get("version", self.version),
                    processing_time_ms=result.get("processing_time_ms", 0)
                )
                
                return ImageDetectionResponse(
                    available=True,
                    result=detection_result,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            raise DetectionError(f"Custom model detection failed: {str(e)}")


# Global instance
image_detector = ImageDetectorService()
