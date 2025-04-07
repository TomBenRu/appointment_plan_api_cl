import calendar
import pprint
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from pony.orm import db_session, desc, get, select, exists

from api.models import schemas
from api.services import CalendarService
from database.models import Appointment as DBAppointment
from database.models import Person as DBPerson
from database.models import LocationOfWork as DBLocationOfWork
from api import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@db_session
def index(request: Request, 
          year: Optional[int] = Query(None),
          month: Optional[int] = Query(None),
          filter_person_id: Optional[str] = Query(None), 
          filter_location_id: Optional[str] = Query(None)):
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
            "all_locations": filter_options["all_locations"]
        }
    )


@router.get("/api/calendar-partial", response_class=HTMLResponse)
@db_session
def calendar_partial(
    request: Request,
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
            "all_locations": filter_options["all_locations"]
        }
    )


@router.get("/api/day-view/{date_str}", response_class=HTMLResponse)
@db_session
def day_view_modal(request: Request, date_str: str):
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
            **day_data  # Entpacke alle Daten aus day_data
        }
    )


@router.get("/plans", response_class=HTMLResponse)
@db_session
def plans(request: Request):
    """Seite mit Plänen."""
    from database.models import Plan as DBPlan
    from database.models import PlanPeriod as DBPlanPeriod
    
    # Alle Pläne aus der Datenbank laden und nach Planperiode gruppieren
    all_plans = DBPlan.select().order_by(lambda p: p.plan_period.start_date)
    plans_data = [schemas.PlanDetail.model_validate(p) for p in all_plans]
    
    # Template rendern
    return templates.TemplateResponse(
        "plans.html",
        {
            "request": request,
            "plans": plans_data
        }
    )


@router.get("/plans/{plan_id}", response_class=HTMLResponse)
@db_session
def plan_detail(request: Request, plan_id: UUID):
    """Detailseite für einen Plan."""
    from database.models import Plan as DBPlan
    
    # Plan aus der Datenbank laden
    plan = DBPlan.get(id=plan_id)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")

    plan_detail = schemas.PlanDetail.model_validate(plan)
    plan_detail.appointments.sort(key=lambda a: (a.date, a.start_time))

    # Template rendern
    return templates.TemplateResponse(
        "plan_detail.html",
        {
            "request": request,
            "plan": plan_detail
        }
    )


@router.get("/locations", response_class=HTMLResponse)
@db_session
def locations(request: Request):
    """Seite mit Arbeitsorten."""
    from database.models import LocationOfWork as DBLocationOfWork
    
    # Alle Arbeitsorte aus der Datenbank laden
    all_locations = DBLocationOfWork.select().order_by(lambda l: l.name)

    locations_data = [schemas.LocationOfWorkDetail.model_validate(l) for l in all_locations]
    
    # Template rendern
    return templates.TemplateResponse(
        "locations.html",
        {
            "request": request,
            "locations": locations_data
        }
    )


@router.get("/locations/{location_id}", response_class=HTMLResponse)
@db_session
def location_detail(request: Request, location_id: UUID):
    """Detailseite für einen Arbeitsort."""
    
    # Arbeitsort aus der Datenbank laden
    location = DBLocationOfWork.get(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Arbeitsort nicht gefunden")
    
    # Aktuelles Datum
    today = date.today()
    
    # Zukünftige Termine für diesen Ort laden
    future_appointments = DBAppointment.select(
        lambda a: a.location.id == location_id and a.date >= today
    ).order_by(lambda a: (a.date, a.start_time))
    
    # Vergangene Termine für diesen Ort laden (letzte 30 Tage)
    past_date = today - timedelta(days=30)
    past_appointments = DBAppointment.select(
        lambda a: a.location.id == location_id and a.date < today and a.date >= past_date
    ).order_by(lambda a: (desc(a.date), a.start_time))  # Absteigend, neueste zuerst

    location_detail = schemas.LocationOfWorkDetail.model_validate(location)
    future_appointments_data = [schemas.AppointmentDetail.model_validate(a) for a in future_appointments]
    past_appointments_data = [schemas.AppointmentDetail.model_validate(a) for a in past_appointments]
    
    # Template rendern
    return templates.TemplateResponse(
        "location_detail.html",
        {
            "request": request,
            "location": location_detail,
            "future_appointments": future_appointments_data,
            "past_appointments": past_appointments_data
        }
    )


@router.get("/persons", response_class=HTMLResponse)
@db_session
def persons(request: Request):
    """Seite mit allen Personen."""
    
    # Alle Personen aus der Datenbank laden
    all_persons = DBPerson.select().order_by(lambda p: (p.l_name, p.f_name))

    persons_data = [schemas.Person.model_validate(p) for p in all_persons]
    
    # Template rendern
    return templates.TemplateResponse(
        "persons.html",
        {
            "request": request,
            "persons": persons_data
        }
    )


@router.get("/api/appointments/{appointment_id}/detail", response_class=HTMLResponse)
@db_session
def appointment_detail_modal(request: Request, appointment_id: UUID):
    """Liefert das Modal-Fragment für Termindetails."""
    
    # Termin aus der Datenbank laden
    appointment = DBAppointment.get(id=appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Termin nicht gefunden")
    
    appointment_detail = schemas.AppointmentDetail.model_validate(appointment)
    
    # Template rendern
    return templates.TemplateResponse(
        "appointment_detail_modal.html",
        {
            "request": request,
            "appointment": appointment_detail
        }
    )

@router.get("/api/close-modal", response_class=HTMLResponse)
def close_modal(request: Request):
    """Schließt das Modal, indem ein leerer String zurückgegeben wird."""
    return ""

@router.get("/persons/{person_id}", response_class=HTMLResponse)
@db_session
def person_detail(request: Request, person_id: UUID):
    """Detailseite für eine Person."""
    from datetime import date
    
    # Person aus der Datenbank laden
    person = DBPerson.get(id=person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person nicht gefunden")
    
    # Aktuelles Datum
    today = date.today()
    
    # Zukünftige Termine für diese Person laden
    future_appointments = DBAppointment.select(
        lambda a: person in a.persons and a.date >= today
    ).order_by(lambda a: (a.date, a.start_time))
    
    # Vergangene Termine für diese Person laden (letzte 30 Tage)
    past_date = today - timedelta(days=30)
    past_appointments = (DBAppointment.select()
                         .filter(lambda a: person in a.persons)
                         .filter(lambda a: a.date < today)
                         .filter(lambda a: a.date >= past_date).order_by(lambda a: (desc(a.date), a.start_time)))
    for appointment in past_appointments:
        print(appointment.date)

    person_detail = schemas.Person.model_validate(person)
    future_appointments_data = [schemas.AppointmentDetail.model_validate(a) for a in future_appointments]
    past_appointments_data = [schemas.AppointmentDetail.model_validate(a) for a in past_appointments]
    
    # Template rendern
    return templates.TemplateResponse(
        "person_detail.html",
        {
            "request": request,
            "person": person_detail,
            "future_appointments": future_appointments_data,
            "past_appointments": past_appointments_data
        }
    )


@router.get("/api/search", response_class=HTMLResponse)
@db_session
def search(
    request: Request,
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
    
    search_term_lower = q.lower()
    
    # Wenn kein Typ angegeben wurde oder explizit nach Terminen gesucht wird
    if type is None or type == "appointment":

        appointments = select(a for a in DBAppointment if
                              # 1. Suche in Notizen (case-insensitive, None-sicher)
                              (a.notes and search_term_lower in a.notes.lower()) or

                              # 2. Suche in verknüpften Personen (case-insensitive, None-sicher für Namen)
                              # Prüfe, ob *mindestens eine* Person existiert, deren Vor- ODER Nachname passt
                              exists(p for p in a.persons if
                                     (p.f_name and search_term_lower in p.f_name.lower()) or
                                     (p.l_name and search_term_lower in p.l_name.lower())
                                     ) or

                              # 3. Suche im Namen des Ortes (case-insensitive, None-sicher für Ort und Name)
                              (
                                      a.location and a.location.name and search_term_lower in a.location.name.lower()) or

                              # 4. Suche in Gästen
                              (
                                      search_term_lower in str(a.guests).lower()
                              )
                              )

        results["appointments"] = [schemas.AppointmentDetail.model_validate(a) for a in appointments.order_by(lambda a: a.date)[:20]]
    
    # Wenn kein Typ angegeben wurde oder explizit nach Personen gesucht wird
    if type is None or type == "person":
        # Suche nach Personen
        persons = DBPerson.select(
            lambda p: search_term_lower in p.f_name.lower() or
                      search_term_lower in p.l_name.lower() or
                      (p.email and search_term_lower in p.email.lower())
        ).order_by(lambda p: (p.l_name, p.f_name))[:20]  # Limit auf 20 Ergebnisse
        
        results["persons"] = [schemas.Person.model_validate(p) for p in persons]
    
    # Wenn kein Typ angegeben wurde oder explizit nach Orten gesucht wird
    if type is None or type == "location":
        # Suche nach Arbeitsorten
        locations = DBLocationOfWork.select(
            lambda l: search_term_lower in l.name.lower() or
                      search_term_lower in l.address.street.lower() or
                      search_term_lower in l.address.city.lower() or
                      search_term_lower in l.address.postal_code.lower()
        ).order_by(lambda l: l.name)[:20]  # Limit auf 20 Ergebnisse
        
        results["locations"] = [schemas.LocationOfWorkDetail.model_validate(l) for l in locations]
    
    # Template rendern
    return templates.TemplateResponse(
        "search_results.html",
        {
            "request": request,
            "query": q,
            "type": type,
            "results": results,
            "total_count": len(results["appointments"]) + len(results["persons"]) + len(results["locations"])
        }
    )
