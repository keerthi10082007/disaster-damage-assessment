"""Damage assessment service"""

import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.damage import DamageAssessmentResult, DamageAssessmentResponse
from app.utils.errors import DamageAssessmentError
import os
import base64


class DamageAssessmentService:
    """Service for damage assessment analysis"""
    
    def __init__(self):
        self.api_url = os.getenv("DAMAGE_API_URL")
        self.api_key = os.getenv("DAMAGE_API_KEY")
        self.model = os.getenv("DAMAGE_MODEL", "damage-assessment-v1")
        self.timeout = 120
    
    async def analyze_damage(self, current_image_url: str, historical_image_url: Optional[str],
                            latitude: float, longitude: float, disaster_type: str,
                            detection_result: Optional[Dict[str, Any]] = None) -> DamageAssessmentResponse:
        """Analyze damage from satellite imagery"""
        
        # Check if damage model is configured
        if not self.api_url or not self.api_key:
            return DamageAssessmentResponse(
                available=False,
                message="Damage assessment model requires configuration.",
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Download images
                current_img_response = await client.get(current_image_url)
                current_img_response.raise_for_status()
                current_image_data = base64.b64encode(current_img_response.content).decode()
                
                historical_image_data = None
                if historical_image_url:
                    try:
                        hist_img_response = await client.get(historical_image_url)
                        hist_img_response.raise_for_status()
                        historical_image_data = base64.b64encode(hist_img_response.content).decode()
                    except:
                        pass
                
                # Prepare payload
                payload = {
                    "current_image": current_image_data,
                    "historical_image": historical_image_data,
                    "latitude": latitude,
                    "longitude": longitude,
                    "disaster_type": disaster_type,
                    "model": self.model,
                    "detection_result": detection_result
                }
                
                # Send to damage model API
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                result = response.json()
                
                # Parse damage assessment result
                damage_result = DamageAssessmentResult(
                    affected_area=result.get("affected_area"),
                    damaged_buildings=result.get("damaged_buildings"),
                    damaged_roads=result.get("damaged_roads"),
                    building_damage_categories=result.get("building_damage_categories"),
                    road_obstruction=result.get("road_obstruction"),
                    accessibility_impact=result.get("accessibility_impact"),
                    critical_infrastructure_impact=result.get("critical_infrastructure_impact"),
                    damage_severity=result.get("damage_severity"),
                    confidence=result.get("confidence"),
                    model=result.get("model", self.model),
                    model_version=result.get("version", "1"),
                    processing_time_ms=result.get("processing_time_ms", 0)
                )
                
                return DamageAssessmentResponse(
                    available=True,
                    result=damage_result,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except httpx.TimeoutException:
            return DamageAssessmentResponse(
                available=False,
                message="Damage assessment service timeout",
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return DamageAssessmentResponse(
                available=False,
                message=f"Damage assessment unavailable: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )


# Global instance
damage_service = DamageAssessmentService()
