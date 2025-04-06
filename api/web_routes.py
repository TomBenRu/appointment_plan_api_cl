import calendar
import pprint
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from pony.orm import db_session, desc, get, select, exists

from api.models import schemas
from database.models import Appointment as DBAppointment
from database.models import Person as DBPerson
from database.models import LocationOfWork as DBLocationOfWork
from api import templates

router = APIRouter()

def get_calendar_data(year: int, month: int) -> List[List[Dict[str, Any]]]:
    """Erstellt die Kalenderdaten für den angegebenen Monat."""
    # Kalenderobjekt erstellen (Woche beginnt mit Montag)
    cal = calendar.Calendar(firstweekday=0)
    
    # Heutiges Datum
    today = date.today()
    
    # Alle Tage des Monats inkl. angrenzender Tage bekommen
    month_days = cal.monthdatescalendar(year, month)
    
    # Ergebnisliste vorbereiten
    calendar_weeks = []
    
    # Alle Tage des Monats mit Terminen befüllen
    for week in month_days:
        week_data = []
        for day in week:
            day_data = {
                "date": day,
                "day": day.day,
                "is_current_month": day.month == month,
                "is_today": day == today,
                "appointments": []  # Wird später befüllt
            }
            week_data.append(day_data)
        calendar_weeks.append(week_data)
    
    return calendar_weeks

def get_month_name(month: int) -> str:
    """Gibt den deutschen Monatsnamen zurück."""
    return {
        1: "Januar", 2: "Februar", 3: "März", 
        4: "April", 5: "Mai", 6: "Juni",
        7: "Juli", 8: "August", 9: "September", 
        10: "Oktober", 11: "November", 12: "Dezember"
    }[month]


@router.get("/", response_class=HTMLResponse)
@db_session
def index(request: Request, 
          year: Optional[int] = Query(None),
          month: Optional[int] = Query(None),
          filter_person_id: Optional[str] = Query(None), 
          filter_location_id: Optional[str] = Query(None)):
    """Homepage mit Kalenderansicht."""
    # Aktuelles Datum
    today = date.today()
    
    # Jahr und Monat aus URL-Parametern übernehmen, wenn vorhanden
    display_year = year or today.year
    display_month = month or today.month
    
    # Sicherstellen, dass Month zwischen 1 und 12 liegt
    if display_month < 1 or display_month > 12:
        display_month = today.month
    
    # Kalenderdaten für den angegebenen Monat erstellen
    calendar_weeks = get_calendar_data(display_year, display_month)
    
    # Termine für den aktuellen Monat laden
    start_date = calendar_weeks[0][0]["date"]  # Erster Tag im Kalender
    end_date = calendar_weeks[-1][-1]["date"]  # Letzter Tag im Kalender
    
    # Basisabfrage
    appointments_query = DBAppointment.select(
        lambda a: a.date >= start_date and a.date <= end_date
    )
    
    # Filterung nach Person
    if filter_person_id:
        try:
            person_uuid = UUID(filter_person_id) if isinstance(filter_person_id, str) else filter_person_id
            person = DBPerson.get(id=person_uuid)
            appointments_query = select(a for a in appointments_query if person in a.persons)
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    # Filterung nach Arbeitsort
    if filter_location_id:
        try:
            location_uuid = UUID(filter_location_id) if isinstance(filter_location_id, str) else filter_location_id
            location = DBLocationOfWork.get(id=location_uuid)
            appointments_query = select(a for a in appointments_query if a.location.id == location_uuid)
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    # Abfrage ausführen
    appointments = list(appointments_query)
    
    # Aktive Filter für die Anzeige speichern
    active_filters = {
        "person": None,
        "location": None
    }
    
    # Namen der gefilterten Entitäten abrufen für die Anzeige
    if filter_person_id:
        try:
            person_uuid = UUID(filter_person_id) if isinstance(filter_person_id, str) else filter_person_id
            person = DBPerson.get(id=person_uuid)
            if person:
                active_filters["person"] = {"id": str(person.id), "name": f"{person.f_name} {person.l_name}"}
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    if filter_location_id:
        try:
            location_uuid = UUID(filter_location_id) if isinstance(filter_location_id, str) else filter_location_id
            location = DBLocationOfWork.get(id=location_uuid)
            if location:
                active_filters["location"] = {"id": str(location.id), "name": location.name}
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    # Termine in den Kalender einfügen
    for appointment in appointments:
        appointment_data = schemas.AppointmentDetail.model_validate(appointment)
        
        # Termin dem entsprechenden Tag zuordnen
        for week in calendar_weeks:
            for day in week:
                if day["date"] == appointment.date:
                    day["appointments"].append(appointment_data)
    
    for week in calendar_weeks:
        for day in week:
            day["appointments"].sort(key=lambda a: (a.start_time, a.delta))
    
    # Alle Personen und Arbeitsorte für Filter-Dropdowns laden
    all_persons = [schemas.Person.model_validate(p) for p in DBPerson.select().order_by(lambda p: (p.l_name, p.f_name))]
    all_locations = [schemas.LocationOfWorkDetail.model_validate(l) for l in DBLocationOfWork.select().order_by(lambda l: l.name)]

    # Template rendern
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": display_year,
            "month": display_month,
            "month_name": get_month_name(display_month),
            "today": today,
            "active_filters": active_filters,
            "filter_person_id": filter_person_id,
            "filter_location_id": filter_location_id,
            "all_persons": all_persons,
            "all_locations": all_locations
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
    # Wenn kein Jahr/Monat übergeben wurde, nehmen wir den aktuellen
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
    
    # Monat basierend auf direction anpassen
    if direction == "today":
        today = date.today()
        year = today.year
        month = today.month
    elif direction == "prev":
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
    elif direction == "next":
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    
    # Kalenderdaten erstellen
    calendar_weeks = get_calendar_data(year, month)
    
    # Termine laden und filtern
    start_date = calendar_weeks[0][0]["date"]
    end_date = calendar_weeks[-1][-1]["date"]
    
    # Basisabfrage
    appointments_query = DBAppointment.select(
        lambda a: a.date >= start_date and a.date <= end_date
    )
    
    # Filterung nach Person
    if filter_person_id:
        try:
            person_uuid = UUID(filter_person_id) if isinstance(filter_person_id, str) else filter_person_id
            person = DBPerson.get(id=person_uuid)
            appointments_query = select(a for a in appointments_query if person in a.persons)
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    # Filterung nach Arbeitsort
    if filter_location_id:
        try:
            location_uuid = UUID(filter_location_id) if isinstance(filter_location_id, str) else filter_location_id
            appointments_query = appointments_query.filter(
                lambda a: a.location.id == location_uuid
            )
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    # Abfrage ausführen
    appointments = list(appointments_query)
    
    # Aktive Filter für die Anzeige speichern
    active_filters = {
        "person": None,
        "location": None
    }
    
    # Namen der gefilterten Entitäten abrufen für die Anzeige
    if filter_person_id:
        try:
            person_uuid = UUID(filter_person_id) if isinstance(filter_person_id, str) else filter_person_id
            person = DBPerson.get(id=person_uuid)
            if person:
                active_filters["person"] = {"id": str(person.id), "name": f"{person.f_name} {person.l_name}"}
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    if filter_location_id:
        try:
            location_uuid = UUID(filter_location_id) if isinstance(filter_location_id, str) else filter_location_id
            location = DBLocationOfWork.get(id=location_uuid)
            if location:
                active_filters["location"] = {"id": str(location.id), "name": location.name}
        except (ValueError, TypeError):
            pass  # Ungültige UUID ignorieren
    
    for appointment in appointments:
        appointment_data = schemas.AppointmentDetail.model_validate(appointment)
        for week in calendar_weeks:
            for day in week:
                if day["date"] == appointment.date:
                    day["appointments"].append(appointment_data)

    # Termine nach Startzeit sortieren
    for week in calendar_weeks:
        for day in week:
            day["appointments"].sort(key=lambda a: (a.start_time, a.delta))

    # Alle Personen und Arbeitsorte für Filter-Dropdowns laden
    all_persons = [schemas.Person.model_validate(p) for p in
                   DBPerson.select().order_by(lambda p: (p.l_name, p.f_name))]
    all_locations = [schemas.LocationOfWorkDetail.model_validate(l) for l in
                     DBLocationOfWork.select().order_by(lambda l: l.name)]
    
    # Template rendern
    return templates.TemplateResponse(
        "calendar_partial.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": year,
            "month": month,
            "month_name": get_month_name(month),
            "today": date.today(),
            "active_filters": active_filters,
            "filter_person_id": filter_person_id,
            "filter_location_id": filter_location_id,
            # Alle Personen und Arbeitsorte für Filter-Dropdowns laden
            "all_persons": all_persons,
            "all_locations": all_locations
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

                              # 4. Suche in Gästen (siehe Diskussion unten)
                              # ... hier kommt die Logik für `guests` hin ...
                              (
                                      search_term_lower in str(a.guests).lower()
                              )
                              )

        results["appointments"] = [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    # Wenn kein Typ angegeben wurde oder explizit nach Personen gesucht wird
    if type is None or type == "person":
        # Suche nach Personen
        persons = DBPerson.select(
            lambda p: search_term_lower in p.f_name.lower() or
                      search_term_lower in p.l_name.lower() or
                      (p.email is not None and search_term_lower in p.email.lower())
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
