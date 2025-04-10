"""
Plan-spezifische Exceptions.
"""
from typing import Optional, Dict
from uuid import UUID

from .base import ResourceNotFoundException, ConflictException, ValidationException


class PlanNotFoundException(ResourceNotFoundException):
    """Exception für nicht gefundene Pläne."""
    
    def __init__(self, plan_id: UUID, message: Optional[str] = None):
        super().__init__(
            resource_type="Plan",
            resource_id=plan_id,
            message=message
        )


class PlanPeriodNotFoundException(ResourceNotFoundException):
    """Exception für nicht gefundene Planperioden."""
    
    def __init__(self, period_id: UUID, message: Optional[str] = None):
        super().__init__(
            resource_type="PlanPeriod",
            resource_id=period_id,
            message=message
        )


class PlanInUseException(ConflictException):
    """Exception für Pläne, die nicht gelöscht werden können, weil sie in Verwendung sind."""
    
    def __init__(self, plan_id: UUID, reference_count: int, message: Optional[str] = None):
        message = message or f"Der Plan mit ID '{plan_id}' kann nicht gelöscht werden, da er von {reference_count} Elementen verwendet wird."
        details = {
            "plan_id": str(plan_id),
            "reference_count": reference_count
        }
        super().__init__(message=message, details=details)


class DuplicatePlanException(ConflictException):
    """Exception für doppelte Pläne."""
    
    def __init__(self, name: str, period_id: UUID, existing_id: UUID, message: Optional[str] = None):
        message = message or f"Ein Plan mit dem Namen '{name}' für die angegebene Periode existiert bereits (ID: {existing_id})."
        details = {
            "name": name,
            "period_id": str(period_id),
            "existing_id": str(existing_id)
        }
        super().__init__(message=message, details=details)


class PlanValidationException(ValidationException):
    """Exception für Validierungsfehler bei Plänen."""
    
    def __init__(self, errors: Dict[str, str], message: Optional[str] = None):
        message = message or "Die Plan-Daten sind ungültig."
        super().__init__(errors=errors, message=message)


class PlanPeriodOverlapException(ConflictException):
    """Exception für sich überlappende Planperioden."""
    
    def __init__(self, name: str, start_date: str, end_date: str, existing_period_id: UUID, message: Optional[str] = None):
        message = message or f"Die Planperiode '{name}' ({start_date} bis {end_date}) überschneidet sich mit einer existierenden Periode (ID: {existing_period_id})."
        details = {
            "name": name,
            "start_date": start_date,
            "end_date": end_date,
            "existing_period_id": str(existing_period_id)
        }
        super().__init__(message=message, details=details)
