"""
Location-spezifische Exceptions.
"""
from typing import Optional, Any, Dict
from uuid import UUID

from .base import ResourceNotFoundException, ConflictException, ValidationException


class LocationNotFoundException(ResourceNotFoundException):
    """Exception für nicht gefundene Arbeitsorte."""
    
    def __init__(self, location_id: UUID, message: Optional[str] = None):
        super().__init__(
            resource_type="LocationOfWork",
            resource_id=location_id,
            message=message
        )


class LocationInUseException(ConflictException):
    """Exception für Arbeitsorte, die nicht gelöscht werden können, weil sie in Verwendung sind."""
    
    def __init__(self, location_id: UUID, reference_count: int, message: Optional[str] = None):
        message = message or f"Der Arbeitsort mit ID '{location_id}' kann nicht gelöscht werden, da er von {reference_count} Terminen verwendet wird."
        details = {
            "location_id": str(location_id),
            "reference_count": reference_count
        }
        super().__init__(message=message, details=details)


class DuplicateLocationException(ConflictException):
    """Exception für doppelte Arbeitsorte."""
    
    def __init__(self, name: str, existing_id: UUID, message: Optional[str] = None):
        message = message or f"Ein Arbeitsort mit dem Namen '{name}' existiert bereits (ID: {existing_id})."
        details = {
            "name": name,
            "existing_id": str(existing_id)
        }
        super().__init__(message=message, details=details)


class LocationValidationException(ValidationException):
    """Exception für Validierungsfehler bei Arbeitsorten."""
    
    def __init__(self, errors: Dict[str, str], message: Optional[str] = None):
        message = message or "Die Arbeitsort-Daten sind ungültig."
        super().__init__(errors=errors, message=message)
