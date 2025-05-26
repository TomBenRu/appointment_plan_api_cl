from typing import Optional

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse

from api.services import AppointmentService, LocationService, PersonService
from api.templates import templates
from api.auth.cookie_auth import require_web_employee
from api.auth.models import User
from api.utils import MenuDisplaySection

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def search(
    request: Request,
    user: Optional[User] = Depends(require_web_employee),
    q: str = Query(..., description="Suchbegriff"),
    type: Optional[str] = Query(None, description="Entitätstyp (appointment, person, location)")
):
    """
    Durchsucht Termine, Personen und Orte nach dem angegebenen Suchbegriff.
    Optional kann die Suche auf einen bestimmten Entitätstyp beschränkt werden.
    """
    results = {
        "appointments": [],
        "persons": [],
        "locations": []
    }
    
    # AppointmentService für die Terminsuche nutzen
    appointment_service = AppointmentService()
    
    # Wenn kein Typ angegeben wurde oder explizit nach Terminen gesucht wird
    if type is None or type == "appointment":
        results["appointments"] = appointment_service.search_appointments(q)
    
    # Wenn kein Typ angegeben wurde oder explizit nach Personen gesucht wird
    if type is None or type == "person":
        # PersonService für die Personensuche nutzen
        person_service = PersonService()
        results["persons"] = person_service.search_persons(q)
    
    # Wenn kein Typ angegeben wurde oder explizit nach Orten gesucht wird
    if type is None or type == "location":
        # LocationService für die Ortssuche nutzen
        location_service = LocationService()
        results["locations"] = location_service.search_locations(q)
    
    # Template rendern
    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "query": q,
            "type": type,
            "results": results,
            "total_count": len(results["appointments"]) + len(results["persons"]) + len(results["locations"]),
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )
