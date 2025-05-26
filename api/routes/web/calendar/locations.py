from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from api.services import LocationService, AppointmentService
from api.templates import templates
from api.auth.cookie_auth import require_web_employee
from api.auth.models import User
from api.utils import MenuDisplaySection

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def locations(
    request: Request,
    user: Optional[User] = Depends(require_web_employee)
):
    """Seite mit Arbeitsorten."""
    # LocationService nutzen, um alle Arbeitsorte zu laden
    location_service = LocationService()
    locations_data = location_service.get_all_locations()
    
    # Template rendern
    return templates.TemplateResponse(
        "locations.html",
        {
            "request": request,
            "locations": locations_data,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )

@router.get("/{location_id}", response_class=HTMLResponse)
def view_location_details(
    request: Request,
    location_id: UUID,
    user: Optional[User] = Depends(require_web_employee)
):
    
    # LocationService und AppointmentService nutzen
    location_service = LocationService()
    appointment_service = AppointmentService()
    
    # Arbeitsort aus dem Service laden
    location_detail = location_service.get_location(location_id)
    if not location_detail:
        raise HTTPException(status_code=404, detail="Arbeitsort nicht gefunden")
    
    # Termine für diesen Ort laden
    future_appointments_data = appointment_service.get_future_appointments_for_location(location_id)
    past_appointments_data = appointment_service.get_past_appointments_for_location(location_id)
    
    # Template rendern
    return templates.TemplateResponse(
        "location_detail.html",
        {
            "request": request,
            "location": location_detail,
            "future_appointments": future_appointments_data,
            "past_appointments": past_appointments_data,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )
