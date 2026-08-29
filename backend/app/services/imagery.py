"""Satellite imagery retrieval service"""

import httpx
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from app.schemas.imagery import SatelliteImageResponse, ImageMetadata
from app.utils.errors import ImageryError
import json


class SatelliteImageryService:
    """Service for retrieving satellite imagery from multiple sources"""
    
    # Planetary Computer STAC endpoint for Sentinel-2 L2A
    PLANETARY_COMPUTER_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
    
    # Sentinel Hub Configuration
    SENTINEL_HUB_CATALOG_URL = "https://services.sentinel-hub.com/api/v1/catalog/1.0.0/search"
    SENTINEL_HUB_PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"
    
    TIMEOUT = 60
    
    async def get_current_imagery(self, latitude: float, longitude: float,
                                 days_back: int = 30) -> SatelliteImageResponse:
        """Get current satellite imagery"""
        
        try:
            # Create bounding box (0.1 degree buffer)
            bbox = self._create_bbox(latitude, longitude, buffer=0.1)
            
            # Try Sentinel Hub first
            result = await self._search_sentinel2(bbox, days_back)
            
            if result:
                return result
            
            # Fallback to Planetary Computer
            result = await self._search_planetary_computer(bbox, days_back, "current")
            return result if result else self._create_unavailable_response()
        
        except Exception as e:
            return self._create_unavailable_response(str(e))
    
    async def get_historical_imagery(self, latitude: float, longitude: float,
                                    target_year: int, target_month: int = 6) -> SatelliteImageResponse:
        """Get historical satellite imagery for a specific period"""
        
        try:
            bbox = self._create_bbox(latitude, longitude, buffer=0.1)
            
            # Create date range around target month
            start_date = f"{target_year}-{target_month:02d}-01"
            end_date = f"{target_year}-{target_month:02d}-28"
            
            # Try Sentinel Hub first
            result = await self._search_sentinel2_historical(bbox, start_date, end_date)
            
            if result:
                return result
            
            # Fallback to Planetary Computer
            result = await self._search_planetary_computer_historical(bbox, start_date, end_date)
            return result if result else self._create_unavailable_response()
        
        except Exception as e:
            return self._create_unavailable_response(str(e))
    
    async def _search_sentinel2(self, bbox: Dict[str, float], days_back: int) -> Optional[SatelliteImageResponse]:
        """Search for recent Sentinel-2 imagery"""
        
        try:
            # Calculate date range
            end_date = datetime.utcnow().date().isoformat()
            start_date = (datetime.utcnow() - timedelta(days=days_back)).date().isoformat()
            
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                # Search using Sentinel Hub API
                search_payload = {
                    "bbox": [bbox["minx"], bbox["miny"], bbox["maxx"], bbox["maxy"]],
                    "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
                    "collections": ["sentinel-2-l2a"],
                    "limit": 10,
                    "filter-lang": "cql-json",
                    "filter": {
                        "type": "and",
                        "args": [
                            {"type": "lte", "args": [{"property": "eo:cloud_cover"}, 50]}
                        ]
                    }
                }
                
                response = await client.post(
                    self.SENTINEL_HUB_CATALOG_URL,
                    json=search_payload
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("features"):
                    # Get the best scene (lowest cloud cover, most recent)
                    features = sorted(
                        data["features"],
                        key=lambda x: (x["properties"].get("eo:cloud_cover", 100), -datetime.fromisoformat(x["properties"].get("datetime", "").replace("Z", "+00:00")).timestamp())
                    )
                    
                    best_scene = features[0]
                    
                    # Get the actual image
                    image_url = await self._render_sentinel2_image(best_scene, bbox)
                    
                    if image_url:
                        return SatelliteImageResponse(
                            available=True,
                            image_url=image_url,
                            metadata=ImageMetadata(
                                acquisition_date=datetime.fromisoformat(best_scene["properties"].get("datetime", "").replace("Z", "+00:00")),
                                source="Sentinel-2 L2A",
                                sensor="MSI",
                                collection="Copernicus",
                                cloud_coverage=best_scene["properties"].get("eo:cloud_cover"),
                                resolution=10.0,
                                latitude=latitude,
                                longitude=longitude,
                                bounding_box=[bbox["minx"], bbox["maxy"], bbox["maxx"], bbox["miny"]],
                                tile_id=best_scene["properties"].get("sentinel:mgrs_tile")
                            ),
                            timestamp=datetime.utcnow().isoformat()
                        )
        
        except Exception as e:
            pass
        
        return None
    
    async def _search_sentinel2_historical(self, bbox: Dict[str, float], 
                                           start_date: str, end_date: str) -> Optional[SatelliteImageResponse]:
        """Search for historical Sentinel-2 imagery"""
        
        # Sentinel-2 started in June 2015, so earlier data won't be available
        year = int(start_date[:4])
        if year < 2015:
            return SatelliteImageResponse(
                available=False,
                message="Sentinel-2 imagery not available before 2015",
                timestamp=datetime.utcnow().isoformat()
            )
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                search_payload = {
                    "bbox": [bbox["minx"], bbox["miny"], bbox["maxx"], bbox["maxy"]],
                    "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
                    "collections": ["sentinel-2-l2a"],
                    "limit": 10
                }
                
                response = await client.post(
                    self.SENTINEL_HUB_CATALOG_URL,
                    json=search_payload
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("features"):
                    features = sorted(
                        data["features"],
                        key=lambda x: x["properties"].get("eo:cloud_cover", 100)
                    )
                    
                    best_scene = features[0]
                    image_url = await self._render_sentinel2_image(best_scene, bbox)
                    
                    if image_url:
                        return SatelliteImageResponse(
                            available=True,
                            image_url=image_url,
                            metadata=ImageMetadata(
                                acquisition_date=datetime.fromisoformat(best_scene["properties"].get("datetime", "").replace("Z", "+00:00")),
                                source="Sentinel-2 L2A",
                                sensor="MSI",
                                collection="Copernicus",
                                cloud_coverage=best_scene["properties"].get("eo:cloud_cover"),
                                resolution=10.0,
                                latitude=latitude,
                                longitude=longitude,
                                bounding_box=[bbox["minx"], bbox["maxy"], bbox["maxx"], bbox["miny"]],
                                tile_id=best_scene["properties"].get("sentinel:mgrs_tile")
                            ),
                            timestamp=datetime.utcnow().isoformat()
                        )
                else:
                    return SatelliteImageResponse(
                        available=False,
                        message="No suitable verified satellite imagery was found for the selected historical period.",
                        timestamp=datetime.utcnow().isoformat()
                    )
        
        except Exception as e:
            return None
    
    async def _search_planetary_computer(self, bbox: Dict[str, float], 
                                        days_back: int, image_type: str = "current") -> Optional[SatelliteImageResponse]:
        """Search using Microsoft Planetary Computer STAC"""
        
        try:
            end_date = datetime.utcnow().date().isoformat()
            start_date = (datetime.utcnow() - timedelta(days=days_back)).date().isoformat()
            
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                search_payload = {
                    "bbox": [bbox["minx"], bbox["miny"], bbox["maxx"], bbox["maxy"]],
                    "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
                    "collections": ["sentinel-2-l2a"],
                    "limit": 10
                }
                
                response = await client.post(
                    f"{self.PLANETARY_COMPUTER_URL}/search",
                    json=search_payload
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("features"):
                    features = sorted(
                        data["features"],
                        key=lambda x: x["properties"].get("eo:cloud_cover", 100)
                    )
                    best_scene = features[0]
                    
                    # Generate asset URL
                    assets = best_scene.get("assets", {})
                    if "thumbnail" in assets:
                        image_url = assets["thumbnail"]["href"]
                        
                        return SatelliteImageResponse(
                            available=True,
                            image_url=image_url,
                            metadata=ImageMetadata(
                                acquisition_date=datetime.fromisoformat(best_scene["properties"].get("datetime", "").replace("Z", "+00:00")),
                                source="Sentinel-2 L2A (Planetary Computer)",
                                sensor="MSI",
                                collection="Copernicus",
                                cloud_coverage=best_scene["properties"].get("eo:cloud_cover"),
                                resolution=10.0,
                                latitude=latitude,
                                longitude=longitude,
                                bounding_box=[bbox["minx"], bbox["maxy"], bbox["maxx"], bbox["miny"]]
                            ),
                            timestamp=datetime.utcnow().isoformat()
                        )
        
        except Exception as e:
            pass
        
        return None
    
    async def _search_planetary_computer_historical(self, bbox: Dict[str, float],
                                                   start_date: str, end_date: str) -> Optional[SatelliteImageResponse]:
        """Search historical imagery on Planetary Computer"""
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                search_payload = {
                    "bbox": [bbox["minx"], bbox["miny"], bbox["maxx"], bbox["maxy"]],
                    "datetime": f"{start_date}T00:00:00Z/{end_date}T23:59:59Z",
                    "collections": ["sentinel-2-l2a"],
                    "limit": 10
                }
                
                response = await client.post(
                    f"{self.PLANETARY_COMPUTER_URL}/search",
                    json=search_payload
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("features"):
                    features = sorted(
                        data["features"],
                        key=lambda x: x["properties"].get("eo:cloud_cover", 100)
                    )
                    best_scene = features[0]
                    assets = best_scene.get("assets", {})
                    
                    if "thumbnail" in assets:
                        image_url = assets["thumbnail"]["href"]
                        
                        return SatelliteImageResponse(
                            available=True,
                            image_url=image_url,
                            metadata=ImageMetadata(
                                acquisition_date=datetime.fromisoformat(best_scene["properties"].get("datetime", "").replace("Z", "+00:00")),
                                source="Sentinel-2 L2A (Planetary Computer)",
                                sensor="MSI",
                                collection="Copernicus",
                                cloud_coverage=best_scene["properties"].get("eo:cloud_cover"),
                                resolution=10.0,
                                latitude=latitude,
                                longitude=longitude,
                                bounding_box=[bbox["minx"], bbox["maxy"], bbox["maxx"], bbox["miny"]]
                            ),
                            timestamp=datetime.utcnow().isoformat()
                        )
                else:
                    return SatelliteImageResponse(
                        available=False,
                        message="No suitable verified satellite imagery was found for the selected historical period.",
                        timestamp=datetime.utcnow().isoformat()
                    )
        
        except Exception as e:
            return None
    
    async def _render_sentinel2_image(self, scene: Dict[str, Any], bbox: Dict[str, float]) -> Optional[str]:
        """Render Sentinel-2 image using Sentinel Hub Process API"""
        # This would require proper authentication
        # For now, return a direct link to the TCI (True Color Image) asset if available
        
        try:
            if "thumbnail" in scene.get("assets", {}):
                return scene["assets"]["thumbnail"]["href"]
        except:
            pass
        
        return None
    
    def _create_bbox(self, latitude: float, longitude: float, buffer: float = 0.1) -> Dict[str, float]:
        """Create bounding box around a point"""
        return {
            "minx": longitude - buffer,
            "miny": latitude - buffer,
            "maxx": longitude + buffer,
            "maxy": latitude + buffer
        }
    
    def _create_unavailable_response(self, message: str = "Satellite imagery unavailable") -> SatelliteImageResponse:
        """Create unavailable response"""
        return SatelliteImageResponse(
            available=False,
            message=message,
            timestamp=datetime.utcnow().isoformat()
        )


# Global instance
imagery_service = SatelliteImageryService()
