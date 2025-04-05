import calendar
import pprint
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from pony.orm import db_session, desc

from api.models import schemas
from database.models import Appointment as DBAppointment
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
def index(request: Request):
    """Homepage mit Kalenderansicht."""
    # Aktuelles Datum
    today = date.today()
    
    # Kalenderdaten für den aktuellen Monat erstellen
    calendar_weeks = get_calendar_data(today.year, today.month)
    
    # Termine für den aktuellen Monat laden
    start_date = calendar_weeks[0][0]["date"]  # Erster Tag im Kalender
    end_date = calendar_weeks[-1][-1]["date"]  # Letzter Tag im Kalender
    
    # Termine aus der Datenbank laden
    appointments = list(DBAppointment.select(
        lambda a: a.date >= start_date and a.date <= end_date
    ))
    
    # Termine in den Kalender einfügen
    for appointment in appointments:
        appointment_data = schemas.AppointmentDetail.model_validate(appointment)
        
        # Termin dem entsprechenden Tag zuordnen
        for week in calendar_weeks:
            for day in week:
                if day["date"] == appointment.date:
                    day["appointments"].append(appointment_data)
    
    # Template rendern
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": today.year,
            "month": today.month,
            "month_name": get_month_name(today.month)
        }
    )


@router.get("/api/calendar-partial", response_class=HTMLResponse)
@db_session
def calendar_partial(
    request: Request,
    direction: str = Query(None, description="Richtung (prev/next)"),
    year: int = Query(None, description="Jahr"),
    month: int = Query(None, description="Monat (1-12)")
):
    """Liefert das Kalender-Partial für einen bestimmten Monat."""
    # Wenn kein Jahr/Monat übergeben wurde, nehmen wir den aktuellen
    if year is None or month is None:
        today = date.today()
        year = today.year
        month = today.month
    
    # Monat basierend auf direction anpassen
    if direction == "prev":
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
    
    # Termine laden und einfügen (wie bisher)
    start_date = calendar_weeks[0][0]["date"]
    end_date = calendar_weeks[-1][-1]["date"]
    appointments = list(DBAppointment.select(
        lambda a: a.date >= start_date and a.date <= end_date
    ))
    
    for appointment in appointments:
        appointment_data = schemas.AppointmentDetail.model_validate(appointment)
        for week in calendar_weeks:
            for day in week:
                if day["date"] == appointment.date:
                    day["appointments"].append(appointment_data)
    
    # Template rendern
    return templates.TemplateResponse(
        "calendar_partial.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": year,
            "month": month,
            "month_name": get_month_name(month)  # Monatsnamen hinzufügen
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
    from database.models import LocationOfWork as DBLocationOfWork
    from database.models import Appointment as DBAppointment
    from datetime import date
    
    # Arbeitsort aus der Datenbank laden
    location = DBLocationOfWork.get(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Arbeitsort nicht gefunden")
    
    # Zukünftige Termine für diesen Ort laden
    today = date.today()
    future_appointments = DBAppointment.select(
        lambda a: a.location.id == location_id and a.date >= today
    ).order_by(lambda a: (a.date, a.start_time))

    location_detail = schemas.LocationOfWorkDetail.model_validate(location)
    appointments_data = [schemas.AppointmentDetail.model_validate(a) for a in future_appointments]
    
    # Template rendern
    return templates.TemplateResponse(
        "location_detail.html",
        {
            "request": request,
            "location": location_detail,
            "appointments": appointments_data
        }
    )


@router.get("/persons", response_class=HTMLResponse)
@db_session
def persons(request: Request):
    """Seite mit allen Personen."""
    from database.models import Person as DBPerson
    
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


@router.get("/persons/{person_id}", response_class=HTMLResponse)
@db_session
def person_detail(request: Request, person_id: UUID):
    """Detailseite für eine Person."""
    from database.models import Person as DBPerson
    from database.models import Appointment as DBAppointment
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
