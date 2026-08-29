"""Zone analysis service"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.zone import Zone, ZoneAnalysisResponse
from math import sqrt


class ZoneAnalysisService:
    """Service for dividing affected areas into analysis zones"""
    
    async def analyze_zones(self, latitude: float, longitude: float,
                           affected_area_km2: Optional[float] = None,
                           population: Optional[int] = None,
                           damage_data: Optional[Dict[str, Any]] = None,
                           infrastructure: Optional[List[Dict[str, Any]]] = None) -> ZoneAnalysisResponse:
        """Divide affected region into zones"""
        
        zones = []
        
        # Create zones based on distance from epicenter
        zone_configs = [
            {"radius_km": 1, "name": "Critical Zone", "id": "Z1"},
            {"radius_km": 5, "name": "High Impact Zone", "id": "Z2"},
            {"radius_km": 15, "name": "Moderate Impact Zone", "id": "Z3"},
        ]
        
        for i, config in enumerate(zone_configs):
            # Calculate area
            zone_area = 3.14159 * (config["radius_km"] ** 2)
            
            # Distribute population proportionally
            zone_population = None
            if population:
                zone_population = int(population * (config["radius_km"] / 15))
            
            # Get infrastructure in this zone
            zone_infrastructure = []
            if infrastructure:
                for infra in infrastructure:
                    dist = sqrt((infra.get("latitude", 0) - latitude)**2 + 
                               (infra.get("longitude", 0) - longitude)**2) * 111
                    if dist <= config["radius_km"]:
                        zone_infrastructure.append(infra.get("name", "Unknown"))
            
            zone = Zone(
                zone_id=config["id"],
                location=f"{config['name']} (0-{config['radius_km']} km from center)",
                affected_area=zone_area,
                population=zone_population,
                buildings=None,
                damaged_buildings=None,
                roads=None,
                road_impact=None,
                infrastructure=zone_infrastructure,
                severity="Critical" if i == 0 else ("High" if i == 1 else "Moderate"),
                accessibility="Severely Limited" if i == 0 else ("Limited" if i == 1 else "Partial")
            )
            zones.append(zone)
        
        return ZoneAnalysisResponse(
            latitude=latitude,
            longitude=longitude,
            zones=zones,
            total_zones=len(zones),
            timestamp=datetime.utcnow().isoformat()
        )


# Global instance
zone_service = ZoneAnalysisService()
