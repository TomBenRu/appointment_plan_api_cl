# Service-Module für die Anwendung

from .calendar_service import CalendarService

# Diese werden später importiert, wenn weitere Service-Klassen implementiert sind
# from .appointment_service import AppointmentService
# from .location_service import LocationService
# from .person_service import PersonService
# from .plan_service import PlanService

__all__ = [
    'CalendarService', 
    # 'AppointmentService', 
    # 'LocationService', 
    # 'PersonService', 
    # 'PlanService'
]
