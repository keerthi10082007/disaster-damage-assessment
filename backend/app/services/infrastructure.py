"""Infrastructure data service using OpenStreetMap"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.infrastructure import InfrastructureFeature, InfrastructureResponse
from math import radians, cos, sin, asin, sqrt


class InfrastructureService:
    """Service for infrastructure data from OpenStreetMap"""
    
    # Overpass API endpoint
    OVERPASS_API = "https://overpass-api.de/api/interpreter"
    TIMEOUT = 30
    
    async def get_nearby_infrastructure(self, latitude: float, longitude: float,
                                       radius_km: int = 10) -> InfrastructureResponse:
        """Get infrastructure features near a location"""
        
        try:
            # Convert radius to degrees (approximate)
            radius_degrees = radius_km / 111.0
            bbox = f"({latitude - radius_degrees},{longitude - radius_degrees},{latitude + radius_degrees},{longitude + radius_degrees})"
            
            features = []
            
            # Query for hospitals
            features.extend(await self._query_overpass(
                bbox, "amenity=hospital", "Hospitals"
            ))
            
            # Query for schools
            features.extend(await self._query_overpass(
                bbox, "amenity=school", "Schools"
            ))
            
            # Query for emergency services
            features.extend(await self._query_overpass(
                bbox, "amenity=fire_station", "Fire Stations"
            ))
            
            # Query for bridges
            features.extend(await self._query_overpass(
                bbox, "man_made=bridge", "Bridges"
            ))
            
            # Calculate distances
            for feature in features:
                feature.distance_km = self._calculate_distance(
                    latitude, longitude, feature.latitude, feature.longitude
                )
            
            # Sort by distance
            features.sort(key=lambda x: x.distance_km)
            
            return InfrastructureResponse(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                features=features[:50],  # Return top 50
                total_count=len(features),
                available=len(features) > 0,
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            return InfrastructureResponse(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                features=[],
                total_count=0,
                available=False,
                message=str(e),
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _query_overpass(self, bbox: str, filter_clause: str, feature_type: str) -> List[InfrastructureFeature]:
        """Query Overpass API for specific features"""
        
        try:
            # Build Overpass QL query
            query = f"""
            [out:json];
            (node[{filter_clause}]{bbox};
            way[{filter_clause}]{bbox};
            relation[{filter_clause}]{bbox};);
            out center;
            """
            
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.post(self.OVERPASS_API, data=query)
                response.raise_for_status()
                data = response.json()
                
                features = []
                for element in data.get("elements", []):
                    if element.get("type") == "node":
                        feature = InfrastructureFeature(
                            name=element.get("tags", {}).get("name", f"{feature_type} #{element.get('id')}"),
                            feature_type=feature_type,
                            latitude=element.get("lat"),
                            longitude=element.get("lon"),
                            distance_km=0,  # Will be calculated later
                            source="OpenStreetMap",
                            osm_id=str(element.get("id"))
                        )
                        features.append(feature)
                    elif element.get("type") in ["way", "relation"]:
                        center = element.get("center", {})
                        if center:
                            feature = InfrastructureFeature(
                                name=element.get("tags", {}).get("name", f"{feature_type} #{element.get('id')}"),
                                feature_type=feature_type,
                                latitude=center.get("lat"),
                                longitude=center.get("lon"),
                                distance_km=0,
                                source="OpenStreetMap",
                                osm_id=str(element.get("id"))
                            )
                            features.append(feature)
                
                return features
        
        except Exception as e:
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r


# Global instance
infrastructure_service = InfrastructureService()
