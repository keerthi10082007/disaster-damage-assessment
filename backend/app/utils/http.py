"""HTTP utility functions"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class HTTPClient:
    """Async HTTP client with timeout and retry support"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def get(self, url: str, headers: Optional[Dict[str, str]] = None, 
                  params: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[Dict]:
        """Make GET request with retry logic"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, headers=headers, params=params, **kwargs)
                    response.raise_for_status()
                    return response.json()
                except httpx.TimeoutException:
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
                except httpx.HTTPError as e:
                    if response.status_code >= 500 and attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise
        return None
    
    async def post(self, url: str, data: Optional[Dict[str, Any]] = None,
                   json: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, **kwargs) -> Optional[Dict]:
        """Make POST request with retry logic"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    response = await client.post(url, data=data, json=json, headers=headers, **kwargs)
                    response.raise_for_status()
                    return response.json()
                except httpx.TimeoutException:
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
                except httpx.HTTPError as e:
                    if response.status_code >= 500 and attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise
        return None
