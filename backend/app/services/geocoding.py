"""Geocoding service using OpenStreetMap Nominatim"""

import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.geocoding import LocationSuggestion, GeocodingSearchResponse
from app.utils.errors import GeocodingError
from app.utils.validation import validate_location_query


class GeocodingService:
    """Service for location geocoding and autocomplete"""
    
    NOMINATIM_API_URL = "https://nominatim.openstreetmap.org"
    # User-Agent required by Nominatim policy
    USER_AGENT = "DisasterAssessmentSystem/1.0 (keerthikuruva77@gmail.com)"
    TIMEOUT = 30
    
    def __init__(self):
        self.session = None
    
    async def search(self, query: str, limit: int = 10) -> GeocodingSearchResponse:
        """Search for locations matching query"""
        
        # Validate query
        is_valid, error_msg = validate_location_query(query)
        if not is_valid:
            return GeocodingSearchResponse(
                success=False,
                results=[],
                error=error_msg,
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    f"{self.NOMINATIM_API_URL}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "limit": limit,
                        "addressdetails": 1,
                        "extratags": 0
                    },
                    headers={"User-Agent": self.USER_AGENT}
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data:
                    suggestion = LocationSuggestion(
                        display_name=item.get("display_name", ""),
                        latitude=float(item.get("lat", 0)),
                        longitude=float(item.get("lon", 0)),
                        country=item.get("address", {}).get("country"),
                        state=item.get("address", {}).get("state"),
                        city=item.get("address", {}).get("city") or item.get("address", {}).get("town"),
                        osm_id=str(item.get("osm_id")),
                        osm_type=item.get("osm_type"),
                        boundingbox=[float(x) for x in item.get("boundingbox", [])] if item.get("boundingbox") else None
                    )
                    results.append(suggestion)
                
                return GeocodingSearchResponse(
                    success=True,
                    results=results,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except httpx.TimeoutException:
            error_msg = "Geocoding service timeout. Please try again."
            raise GeocodingError(error_msg)
        except httpx.HTTPError as e:
            error_msg = f"Geocoding service error: {str(e)}"
            raise GeocodingError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in geocoding: {str(e)}"
            raise GeocodingError(error_msg)
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Reverse geocode coordinates to location name"""
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    f"{self.NOMINATIM_API_URL}/reverse",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "format": "json",
                        "addressdetails": 1
                    },
                    headers={"User-Agent": self.USER_AGENT}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise GeocodingError(f"Reverse geocoding failed: {str(e)}")


# Global instance
geocode_service = GeocodingService()
