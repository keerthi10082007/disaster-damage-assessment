"""Disaster event service using NASA EONET API"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.schemas.disaster import DisasterEvent, DisasterEventResponse
from app.utils.errors import DisasterEventError
import os


class DisasterEventService:
    """Service for fetching disaster events from NASA EONET"""
    
    # NASA EONET API (no API key required for basic queries)
    EONET_API_URL = "https://eonet.gsfc.nasa.gov/api/v3"
    TIMEOUT = 30
    
    # Disaster type mappings
    DISASTER_TYPES = {
        "Floods": "Flood",
        "Wildfires": "Wildfire",
        "Cyclones": "Cyclone",
        "Landslides": "Landslide",
        "Severe Storms": "Severe Storm",
        "Volcanoes": "Volcano",
        "Earthquakes": "Earthquake"
    }
    
    async def get_nearby_events(self, latitude: float, longitude: float, 
                               radius_km: int = 100) -> DisasterEventResponse:
        """Get disaster events near a location"""
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                # Get all active events
                response = await client.get(
                    f"{self.EONET_API_URL}/events",
                    params={
                        "status": "open",
                        "limit": 100
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                events = []
                
                if data.get("events"):
                    for event in data["events"]:
                        # Get event location
                        if event.get("geometries"):
                            for geom in event["geometries"]:
                                if geom.get("type") == "Point":
                                    coords = geom.get("coordinates", [None, None])
                                    if len(coords) >= 2:
                                        event_lon, event_lat = coords[0], coords[1]
                                        
                                        # Calculate distance
                                        distance = self._calculate_distance(
                                            latitude, longitude, event_lat, event_lon
                                        )
                                        
                                        # Only include if within radius
                                        if distance <= radius_km:
                                            # Get event type
                                            event_type = "Unknown"
                                            if event.get("categories"):
                                                category_id = event["categories"][0].get("id", "")
                                                event_type = self.DISASTER_TYPES.get(category_id, category_id)
                                            
                                            disaster = DisasterEvent(
                                                id=event.get("id", ""),
                                                title=event.get("title", ""),
                                                description=event.get("description"),
                                                event_type=event_type,
                                                latitude=event_lat,
                                                longitude=event_lon,
                                                date=datetime.fromisoformat(event["geometries"][0].get("date", "").replace("Z", "+00:00")),
                                                source="NASA EONET",
                                                distance_km=round(distance, 2)
                                            )
                                            events.append(disaster)
                
                # Sort by distance
                events.sort(key=lambda x: x.distance_km)
                
                status = "Active Event" if events else "No Active Event"
                
                return DisasterEventResponse(
                    success=True,
                    status=status,
                    events=events[:10],  # Return top 10 closest
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except httpx.TimeoutException:
            raise DisasterEventError("NASA EONET service timeout")
        except httpx.HTTPError as e:
            return DisasterEventResponse(
                success=False,
                status="Data Unavailable",
                events=[],
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                error="Disaster data unavailable",
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            return DisasterEventResponse(
                success=False,
                status="Data Unavailable",
                events=[],
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                error=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (in km)"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r


# Global instance
disaster_service = DisasterEventService()
