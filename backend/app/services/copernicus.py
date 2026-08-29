"""Copernicus authentication and Sentinel Hub integration"""

import httpx
import base64
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.utils.errors import ApplicationError
import os
from functools import lru_cache


class CopernicusAuthService:
    """Authentication for Copernicus Data Space Ecosystem"""
    
    AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    CATALOG_API_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"
    SENTINEL_HUB_URL = "https://services.sentinel-hub.com/api/v1/process"
    
    def __init__(self):
        self.client_id = os.getenv("COPERNICUS_CLIENT_ID")
        self.client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> Optional[str]:
        """Get OAuth2 access token from Copernicus"""
        
        if not self.client_id or not self.client_secret:
            raise ApplicationError(
                "Copernicus credentials not configured. Set COPERNICUS_CLIENT_ID and COPERNICUS_CLIENT_SECRET.",
                500
            )
        
        # Check if token is still valid
        if self.access_token and self.token_expires_at and datetime.utcnow() < self.token_expires_at:
            return self.access_token
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.AUTH_URL,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                self.access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
                
                return self.access_token
        
        except httpx.HTTPError as e:
            raise ApplicationError(f"Failed to authenticate with Copernicus: {str(e)}", 503)
    
    async def search_sentinel2_scenes(self, bbox: str, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """Search for Sentinel-2 L2A scenes in catalog"""
        
        token = await self.get_access_token()
        
        if not token:
            raise ApplicationError("Unable to authenticate with Copernicus", 503)
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # OData query for Sentinel-2 L2A
                query = f"""
                Collections('SENTINEL2')/Products?$filter=
                OData.CSC.Intersects(area=geography'SRID=4326;{bbox}')
                and Attributes/OData.CSC.StringAttribute/any(a:a/Name eq 'processingLevel' and a/OData.CSC.StringAttribute/Value eq 'Level-2A')
                and ContentDate/Start gt {start_date}T00:00:00Z
                and ContentDate/Start lt {end_date}T23:59:59Z
                &$top=100&$orderby=ContentDate/Start desc
                """
                
                response = await client.get(
                    f"{self.CATALOG_API_URL}/{query}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                response.raise_for_status()
                return response.json()
        
        except Exception as e:
            raise ApplicationError(f"Failed to search Sentinel-2 scenes: {str(e)}", 503)


class SentinelHubService:
    """Sentinel Hub Process API for rendering satellite imagery"""
    
    API_URL = "https://services.sentinel-hub.com/api/v1/process"
    
    def __init__(self):
        self.client_id = os.getenv("SENTINEL_HUB_CLIENT_ID")
        self.client_secret = os.getenv("SENTINEL_HUB_CLIENT_SECRET")
        self.instance_id = os.getenv("SENTINEL_HUB_INSTANCE_ID")
    
    async def get_true_color_image(self, bbox: Dict[str, float], start_date: str, end_date: str,
                                   width: int = 512, height: int = 512) -> Optional[bytes]:
        """Get true color (natural color) image from Sentinel-2"""
        
        if not self.instance_id:
            raise ApplicationError("Sentinel Hub instance ID not configured", 500)
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                # Sentinel Hub evalscript for true color (B04, B03, B02)
                evalscript = """
                //VERSION=3
                function setup() {
                  return {
                    input: [{
                      bands: ["B02", "B03", "B04", "dataMask"],
                      units: "DN"
                    }],
                    output: {
                      bands: 3,
                      sampleType: "UINT8"
                    }
                  };
                }
                
                function evaluatePixel(sample) {
                  let factor = 255 / 10000;
                  let red = sample.B04 * factor;
                  let green = sample.B03 * factor;
                  let blue = sample.B02 * factor;
                  
                  return [red, green, blue];
                }
                """
                
                payload = {
                    "input": {
                        "bounds": {
                            "bbox": [
                                bbox["minx"],
                                bbox["miny"],
                                bbox["maxx"],
                                bbox["maxy"]
                            ],
                            "properties": {"crs": "http://www.opengis.net/gml/srs/epsg.xml#4326"}
                        },
                        "data": [{
                            "type": "sentinel-2-l2a",
                            "dataFilter": {
                                "timeRange": {
                                    "from": f"{start_date}T00:00:00Z",
                                    "to": f"{end_date}T23:59:59Z"
                                },
                                "maxCloudCoverage": 50
                            }
                        }]
                    },
                    "evalscript": evalscript,
                    "output": {
                        "width": width,
                        "height": height,
                        "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
                    }
                }
                
                # Note: This requires proper authentication setup
                # For now, this is the correct structure
                response = await client.post(
                    self.API_URL,
                    json=payload,
                    auth=(self.client_id, self.client_secret)
                )
                response.raise_for_status()
                return response.content
        
        except Exception as e:
            raise ApplicationError(f"Failed to get image from Sentinel Hub: {str(e)}", 503)


# Global instances
copernicus_auth = CopernicusAuthService()
sentinel_hub = SentinelHubService()
