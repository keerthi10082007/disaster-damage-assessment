"""Custom error classes for the application"""

class ApplicationError(Exception):
    """Base application error"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class GeocodingError(ApplicationError):
    """Geocoding service error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 400, details)


class DisasterEventError(ApplicationError):
    """Disaster event API error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class ImageryError(ApplicationError):
    """Satellite imagery error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class DetectionError(ApplicationError):
    """Image detection error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class DamageAssessmentError(ApplicationError):
    """Damage assessment error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class AIError(ApplicationError):
    """AI service error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 503, details)


class ConfigurationError(ApplicationError):
    """Configuration error"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 500, details)
