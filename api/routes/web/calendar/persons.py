from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from api.services import PersonService, AppointmentService
from api.templates import templates
from api.auth.cookie_auth import require_web_employee
from api.auth.models import User
from api.utils import MenuDisplaySection

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def persons(
    request: Request,
    user: Optional[User] = Depends(require_web_employee)
):
    """Seite mit allen Personen."""
    
    # PersonService nutzen, um alle Personen zu laden
    person_service = PersonService()
    persons_data = person_service.get_all_persons()
    
    # Template rendern
    return templates.TemplateResponse(
        "persons.html",
        {
            "request": request,
            "persons": persons_data,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )

@router.get("/{person_id}", response_class=HTMLResponse)
def person_detail(
    request: Request, 
    person_id: UUID,
    user: Optional[User] = Depends(require_web_employee)
):
    """Detailseite für eine Person."""
    
    # PersonService und AppointmentService nutzen
    person_service = PersonService()
    appointment_service = AppointmentService()
    
    # Person aus dem Service laden
    person_detail = person_service.get_person(person_id)
    if not person_detail:
        raise HTTPException(status_code=404, detail="Person nicht gefunden")
    
    # Termine für diese Person laden
    future_appointments_data = appointment_service.get_future_appointments_for_person(person_id)
    past_appointments_data = appointment_service.get_past_appointments_for_person(person_id)
    
    # Template rendern
    return templates.TemplateResponse(
        "person_detail.html",
        {
            "request": request,
            "person": person_detail,
            "future_appointments": future_appointments_data,
            "past_appointments": past_appointments_data,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )
