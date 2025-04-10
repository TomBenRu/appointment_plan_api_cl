"""
Basisklassen für Exceptions im Terminkalender-Projekt.

Diese Klassen bieten eine Hierarchie von Exceptions, die in den Services
und API-Endpunkten verwendet werden können, um Fehler konsistent zu behandeln.
"""
from typing import Dict, Any, Optional
from fastapi import status


class AppBaseException(Exception):
    """Basisklasse für alle anwendungsspezifischen Exceptions."""
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Ein interner Fehler ist aufgetreten."
    
    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialisiert die Exception mit optionalen Parametern.
        
        Args:
            message: Eine benutzerfreundliche Fehlermeldung.
            status_code: HTTP-Statuscode für die Antwort.
            details: Zusätzliche Details zum Fehler.
        """
        self.message = message or self.default_message
        self.status_code = status_code or self.status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Gibt ein Dictionary mit den Exception-Details zurück.
        
        Returns:
            Dict mit den Exception-Details.
        """
        return {
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class ResourceNotFoundException(AppBaseException):
    """Exception für nicht gefundene Ressourcen."""
    
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Die angeforderte Ressource wurde nicht gefunden."
    
    def __init__(self, resource_type: str, resource_id: Any, message: Optional[str] = None, **kwargs):
        """
        Initialisiert die ResourceNotFoundException.
        
        Args:
            resource_type: Typ der Ressource (z.B. "Appointment", "Person").
            resource_id: ID der nicht gefundenen Ressource.
            message: Optionale benutzerdefinierte Fehlermeldung.
            **kwargs: Weitere optionale Parameter für die Basisklasse.
        """
        details = kwargs.pop("details", {})
        details.update({
            "resource_type": resource_type,
            "resource_id": str(resource_id)
        })
        message = message or f"{resource_type} mit ID '{resource_id}' wurde nicht gefunden."
        super().__init__(message=message, details=details, **kwargs)


class ValidationException(AppBaseException):
    """Exception für Validierungsfehler."""
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Die Eingabedaten sind ungültig."
    
    def __init__(self, errors: Dict[str, str], message: Optional[str] = None, **kwargs):
        """
        Initialisiert die ValidationException.
        
        Args:
            errors: Dict mit Feldnamen als Schlüssel und Fehlermeldungen als Werte.
            message: Optionale benutzerdefinierte Fehlermeldung.
            **kwargs: Weitere optionale Parameter für die Basisklasse.
        """
        details = kwargs.pop("details", {})
        details.update({"validation_errors": errors})
        super().__init__(message=message, details=details, **kwargs)


class ConflictException(AppBaseException):
    """Exception für Konflikte (z.B. doppelte Einträge, Terminüberschneidungen)."""
    
    status_code = status.HTTP_409_CONFLICT
    default_message = "Die Anfrage konnte aufgrund eines Konflikts nicht ausgeführt werden."


class PermissionDeniedException(AppBaseException):
    """Exception für fehlende Berechtigungen."""
    
    status_code = status.HTTP_403_FORBIDDEN
    default_message = "Sie haben keine Berechtigung für diese Aktion."


class ServiceException(AppBaseException):
    """
    Exception für Fehler in externen Diensten oder internen Komponenten.
    """
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_message = "Ein Fehler ist im Service aufgetreten."
