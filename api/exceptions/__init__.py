from .base import (
    AppBaseException, ResourceNotFoundException, ValidationException,
    ConflictException, PermissionDeniedException, ServiceException
)
from .appointment import (
    AppointmentNotFoundException, AppointmentOverlapException,
    InvalidAppointmentDateException, AppointmentUpdateConflictException
)
from .location import (
    LocationNotFoundException, LocationInUseException,
    DuplicateLocationException, LocationValidationException
)
from .person import (
    PersonNotFoundException, PersonInUseException,
    DuplicatePersonException, PersonValidationException
)
from .plan import (
    PlanNotFoundException, PlanPeriodNotFoundException, PlanInUseException,
    DuplicatePlanException, PlanValidationException, PlanPeriodOverlapException
)

__all__ = [
    # Base exceptions
    'AppBaseException',
    'ResourceNotFoundException',
    'ValidationException',
    'ConflictException',
    'PermissionDeniedException',
    'ServiceException',
    
    # Appointment exceptions
    'AppointmentNotFoundException',
    'AppointmentOverlapException',
    'InvalidAppointmentDateException',
    'AppointmentUpdateConflictException',
    
    # Location exceptions
    'LocationNotFoundException',
    'LocationInUseException',
    'DuplicateLocationException',
    'LocationValidationException',
    
    # Person exceptions
    'PersonNotFoundException',
    'PersonInUseException',
    'DuplicatePersonException',
    'PersonValidationException',
    
    # Plan exceptions
    'PlanNotFoundException',
    'PlanPeriodNotFoundException',
    'PlanInUseException',
    'DuplicatePlanException',
    'PlanValidationException',
    'PlanPeriodOverlapException'
]
