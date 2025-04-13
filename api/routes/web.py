from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse

from api.services import CalendarService, AppointmentService, LocationService, PersonService, PlanService
from api.templates import templates
from api.auth.cookie_auth import require_web_employee, get_current_user_from_cookie
from api.auth.models import User

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request, 
    user: Optional[User] = Depends(require_web_employee),
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    filter_person_id: Optional[str] = Query(None), 
    filter_location_id: Optional[str] = Query(None)
):
    """Homepage mit Kalenderansicht."""
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
            "user": user
        }
    )


@router.get("/hx/calendar-partial", response_class=HTMLResponse)
async def calendar_partial(
    request: Request,
    user: Optional[User] = Depends(get_current_user_from_cookie),
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
async def day_view_modal(
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


@router.get("/plans", response_class=HTMLResponse)
async def plans(
    request: Request,
    user: Optional[User] = Depends(require_web_employee)
):
    """Seite mit Plänen."""
    # PlanService nutzen, um alle Pläne zu laden
    plan_service = PlanService()
    plans_data = plan_service.get_all_plans()
    
    # Template rendern
    return templates.TemplateResponse(
        "plans.html",
        {
            "request": request,
            "plans": plans_data,
            "user": user
        }
    )


@router.get("/plans/{plan_id}", response_class=HTMLResponse)
async def plan_detail(
    request: Request, 
    plan_id: UUID,
    user: Optional[User] = Depends(require_web_employee)
):
    """Detailseite für einen Plan."""
    # PlanService nutzen, um Plandetails zu laden
    plan_service = PlanService()
    plan_detail = plan_service.get_plan_detail(plan_id)

    if not plan_detail:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")

    # Template rendern
    return templates.TemplateResponse(
        "plan_detail.html",
        {
            "request": request,
            "plan": plan_detail,
            "user": user
        }
    )


@router.get("/locations", response_class=HTMLResponse)
async def locations(
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
            "user": user
        }
    )


@router.get("/locations/{location_id}", response_class=HTMLResponse)
async def location_detail(
    request: Request, 
    location_id: UUID,
    user: Optional[User] = Depends(require_web_employee)
):
    """Detailseite für einen Arbeitsort."""
    
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
            "user": user
        }
    )


@router.get("/persons", response_class=HTMLResponse)
async def persons(
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
            "user": user
        }
    )


@router.get("/hx/appointments/{appointment_id}/detail", response_class=HTMLResponse)
async def appointment_detail_modal(
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
async def close_modal(request: Request):
    """Schließt das Modal, indem ein leerer String zurückgegeben wird."""
    return ""

@router.get("/persons/{person_id}", response_class=HTMLResponse)
async def person_detail(
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
            "user": user
        }
    )


@router.get("/search", response_class=HTMLResponse)
async def search(
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
            "user": user
        }
    )
