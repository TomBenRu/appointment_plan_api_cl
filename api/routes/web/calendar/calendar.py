from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse

from api.services import CalendarService, AppointmentService
from api.templates import templates
from api.auth.cookie_auth import require_web_employee
from api.auth.models import User
from api.utils import MenuDisplaySection

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def calendar_index(
    request: Request, 
    user: Optional[User] = Depends(require_web_employee),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    filter_person_id: Optional[str] = Query(None), 
    filter_location_id: Optional[str] = Query(None)
):
    """Kalenderansicht."""
    # Initialisiere den CalendarService
    calendar_service = CalendarService()
    
    # Aktuelles Datum
    today = date.today()
    
    # Jahr und Monat aus URL-Parametern übernehmen, wenn vorhanden
    display_year = year or today.year
    display_month = month or today.month
    
    # Sicherstellen, dass Month zwischen 1 und 12 liegt
    if display_month < 1 or display_month > 12:
        display_month = today.month
    
    # Kalenderdaten für den angegebenen Monat erstellen
    calendar_weeks = calendar_service.get_calendar_data(display_year, display_month)
    
    # Termine in den Kalender einfügen mit optionalen Filtern
    calendar_weeks = calendar_service.fill_calendar_with_appointments(
        calendar_weeks, 
        filter_person_id=filter_person_id, 
        filter_location_id=filter_location_id
    )
    
    # Aktive Filter für die Anzeige ermitteln
    active_filters = calendar_service.get_active_filters(
        filter_person_id=filter_person_id,
        filter_location_id=filter_location_id
    )
    
    # Filter-Optionen laden
    filter_options = calendar_service.get_filter_options()
    
    # Prüfen, ob login_modal angezeigt werden soll
    show_login_modal = getattr(request.state, "show_login_modal", False)
    required_role = getattr(request.state, "required_role", None)
    
    # Template rendern
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": display_year,
            "month": display_month,
            "month_name": calendar_service.get_month_name(display_month),
            "today": today,
            "active_filters": active_filters,
            "filter_person_id": filter_person_id,
            "filter_location_id": filter_location_id,
            "all_persons": filter_options["all_persons"],
            "all_locations": filter_options["all_locations"],
            "show_login_modal": show_login_modal,
            "required_role": required_role,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )


@router.get("/hx/calendar-partial", response_class=HTMLResponse)
def calendar_partial(
    request: Request,
    user: Optional[User] = Depends(require_web_employee),
    direction: str = Query(None, description="Richtung (prev/next/today)"),
    year: int = Query(None, description="Jahr"),
    month: int = Query(None, description="Monat (1-12)"),
    filter_person_id: Optional[str] = Query(None, description="Person-ID für Filterung"),
    filter_location_id: Optional[str] = Query(None, description="Arbeitsort-ID für Filterung")
):
    """Liefert das Kalender-Partial für einen bestimmten Monat."""
    # Initialisiere den CalendarService
    calendar_service = CalendarService()
    
    # Wenn kein Jahr/Monat übergeben wurde, nehmen wir den aktuellen
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
    
    # Monat basierend auf direction anpassen
    date_info = calendar_service.adjust_month(year, month, direction)
    year = date_info["year"]
    month = date_info["month"]
    
    # Kalenderdaten erstellen
    calendar_weeks = calendar_service.get_calendar_data(year, month)
    
    # Termine in den Kalender einfügen mit optionalen Filtern
    calendar_weeks = calendar_service.fill_calendar_with_appointments(
        calendar_weeks, 
        filter_person_id=filter_person_id, 
        filter_location_id=filter_location_id
    )
    
    # Aktive Filter für die Anzeige ermitteln
    active_filters = calendar_service.get_active_filters(
        filter_person_id=filter_person_id,
        filter_location_id=filter_location_id
    )
    
    # Filter-Optionen laden
    filter_options = calendar_service.get_filter_options()
    
    # Template rendern
    return templates.TemplateResponse(
        "calendar_partial.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": year,
            "month": month,
            "month_name": calendar_service.get_month_name(month),
            "today": date.today(),
            "active_filters": active_filters,
            "filter_person_id": filter_person_id,
            "filter_location_id": filter_location_id,
            "all_persons": filter_options["all_persons"],
            "all_locations": filter_options["all_locations"],
            "user": user
        }
    )


@router.get("/hx/day-view/{date_str}", response_class=HTMLResponse)
def day_view_modal(
    request: Request, 
    date_str: str,
    user: Optional[User] = Depends(require_web_employee)
):
    """Liefert das Modal-Fragment für die Tagesansicht."""
    # Initialisiere den CalendarService
    calendar_service = CalendarService()
    
    # Tagesansichtsdaten abrufen
    day_data = calendar_service.get_day_view_data(date_str)
    
    # Fehlerprüfung
    if "error" in day_data:
        raise HTTPException(status_code=400, detail=day_data["error"])
    
    # Template rendern
    return templates.TemplateResponse(
        "day_view_modal.html",
        {
            "request": request,
            **day_data,  # Entpacke alle Daten aus day_data
            "user": user
        }
    )

@router.get("/hx/appointments/{appointment_id}/detail", response_class=HTMLResponse)
def appointment_detail_modal(
    request: Request, 
    appointment_id: UUID,
    user: Optional[User] = Depends(require_web_employee)
):
    """Liefert das Modal-Fragment für Termindetails."""
    
    # AppointmentService nutzen
    appointment_service = AppointmentService()
    appointment_detail = appointment_service.get_appointment_detail(appointment_id)
    
    if not appointment_detail:
        raise HTTPException(status_code=404, detail="Termin nicht gefunden")
    
    # Template rendern
    return templates.TemplateResponse(
        "appointment_detail_modal.html",
        {
            "request": request,
            "appointment": appointment_detail,
            "user": user
        }
    )

@router.get("/hx/close-modal", response_class=HTMLResponse)
def close_modal(
    request: Request,
    user: Optional[User] = Depends(require_web_employee)
):
    """Schließt das Modal, indem ein leerer String zurückgegeben wird."""
    return ""
