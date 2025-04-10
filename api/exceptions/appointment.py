"""
Appointment-spezifische Exceptions.
"""
from typing import Optional, List, Any, Dict
from datetime import date, time
from uuid import UUID

from .base import AppBaseException, ConflictException, ValidationException


class AppointmentNotFoundException(AppBaseException):
    """Exception für nicht gefundene Termine."""
    
    def __init__(self, appointment_id: UUID):
        super().__init__(
            status_code=404,
            message=f"Der Termin mit der ID '{appointment_id}' wurde nicht gefunden."
        )


class AppointmentOverlapException(ConflictException):
    """Exception für sich überlappende Termine."""
    
    def __init__(
        self,
        date_value: date,
        start_time: time,
        end_time: time,
        overlapping_appointments: Optional[List[Dict[str, Any]]] = None
    ):
        details = {
            "date": str(date_value),
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M")
        }
        
        if overlapping_appointments:
            details["overlapping_appointments"] = overlapping_appointments
        
        super().__init__(
            message=f"Der Termin am {date_value} von {start_time.strftime('%H:%M')} bis {end_time.strftime('%H:%M')} "
                    f"überschneidet sich mit existierenden Terminen.",
            details=details
        )


class InvalidAppointmentDateException(ValidationException):
    """Exception für ungültige Terminsdaten."""
    
    def __init__(self, message: str, field: str, value: Any):
        errors = {field: message}
        super().__init__(
            message=message,
            errors=errors,
            details={"invalid_value": str(value)}
        )


class AppointmentUpdateConflictException(ConflictException):
    """Exception für Konflikte beim Aktualisieren von Terminen."""
    
    def __init__(self, appointment_id: UUID, conflicting_field: str, message: Optional[str] = None):
        message = message or f"Konflikt beim Aktualisieren des Termins mit ID '{appointment_id}'."
        details = {
            "appointment_id": str(appointment_id),
            "conflicting_field": conflicting_field
        }
        super().__init__(message=message, details=details)
