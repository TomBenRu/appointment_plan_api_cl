"""
Person-spezifische Exceptions.
"""
from typing import Optional, Dict
from uuid import UUID

from .base import ResourceNotFoundException, ConflictException, ValidationException


class PersonNotFoundException(ResourceNotFoundException):
    """Exception für nicht gefundene Personen."""
    
    def __init__(self, person_id: UUID, message: Optional[str] = None):
        super().__init__(
            resource_type="Person",
            resource_id=person_id,
            message=message
        )


class PersonInUseException(ConflictException):
    """Exception für Personen, die nicht gelöscht werden können, weil sie in Verwendung sind."""
    
    def __init__(self, person_id: UUID, appointment_count: int, message: Optional[str] = None):
        message = message or f"Die Person mit ID '{person_id}' kann nicht gelöscht werden, da sie in {appointment_count} Terminen vorkommt."
        details = {
            "person_id": str(person_id),
            "appointment_count": appointment_count
        }
        super().__init__(message=message, details=details)


class DuplicatePersonException(ConflictException):
    """Exception für doppelte Personen (gleicher Name und E-Mail)."""
    
    def __init__(self, f_name: str, l_name: str, email: Optional[str], existing_id: UUID, message: Optional[str] = None):
        name = f"{f_name} {l_name}"
        message = message or f"Eine Person mit dem Namen '{name}' und der E-Mail '{email or 'keine'}' existiert bereits (ID: {existing_id})."
        details = {
            "name": name,
            "email": email,
            "existing_id": str(existing_id)
        }
        super().__init__(message=message, details=details)


class PersonValidationException(ValidationException):
    """Exception für Validierungsfehler bei Personen."""
    
    def __init__(self, errors: Dict[str, str], message: Optional[str] = None):
        message = message or "Die Personen-Daten sind ungültig."
        super().__init__(errors=errors, message=message)
