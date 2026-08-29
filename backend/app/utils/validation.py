"""Validation utilities"""

import re
from typing import Tuple


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """Validate latitude and longitude values"""
    if not -90 <= latitude <= 90:
        return False, "Latitude must be between -90 and 90"
    if not -180 <= longitude <= 180:
        return False, "Longitude must be between -180 and 180"
    return True, ""


def validate_location_query(query: str) -> Tuple[bool, str]:
    """Validate location search query"""
    if not query or len(query.strip()) < 2:
        return False, "Query must be at least 2 characters"
    if len(query) > 255:
        return False, "Query must be less than 255 characters"
    return True, ""


def validate_date_format(date_str: str) -> Tuple[bool, str]:
    """Validate date format (YYYY-MM-DD)"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False, "Date must be in YYYY-MM-DD format"
    return True, ""
