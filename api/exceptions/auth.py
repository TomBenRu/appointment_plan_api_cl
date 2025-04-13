from uuid import UUID
from fastapi import status
from api.exceptions.base import AppBaseException

class AuthenticationException(AppBaseException):
    """Exception für Authentifizierungsfehler."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Authentifizierung fehlgeschlagen."

class UserNotFoundException(AppBaseException):
    """Exception für nicht gefundene Benutzer."""
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Benutzer wurde nicht gefunden."
    
    def __init__(self, username: str, **kwargs):
        details = kwargs.pop("details", {})
        details.update({"username": username})
        super().__init__(details=details, **kwargs)

class DuplicateUsernameException(AppBaseException):
    """Exception für bereits existierende Benutzernamen."""
    status_code = status.HTTP_409_CONFLICT
    default_message = "Benutzername ist bereits vergeben."
    
    def __init__(self, username: str, **kwargs):
        details = kwargs.pop("details", {})
        details.update({"username": username})
        super().__init__(details=details, **kwargs)

class PersonNotFoundException(AppBaseException):
    """Exception für nicht gefundene Personen."""
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Person wurde nicht gefunden."
    
    def __init__(self, person_id: UUID, **kwargs):
        details = kwargs.pop("details", {})
        details.update({"person_id": str(person_id)})
        super().__init__(details=details, **kwargs)