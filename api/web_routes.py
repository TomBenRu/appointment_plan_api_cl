import calendar
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from pony.orm import db_session

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
        # Pydantic-Schema erstellen und end_time_str hinzufügen
        appointment_data = schemas.Appointment.model_validate(appointment)
        
        # In ein Wörterbuch konvertieren für die Verarbeitung im Template
        try:
            # Pydantic v2 verwendet model_dump() statt dict()
            appointment_data_dict = appointment_data.model_dump()
        except AttributeError:
            # Fallback für ältere Pydantic-Versionen
            appointment_data_dict = appointment_data.dict()
        
        # get_end_time_str Methode zum Dictionary hinzufügen
        appointment_data_dict["get_end_time_str"] = appointment_data.get_end_time_str
        
        # Datum des Termins
        appointment_date = appointment_data.date
        
        # Termin dem entsprechenden Tag zuordnen
        for week in calendar_weeks:
            for day in week:
                if day["date"] == appointment_date:
                    day["appointments"].append(appointment_data_dict)
    
    # Template rendern
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks,
            "year": today.year,
            "month": today.month
        }
    )


@router.get("/api/calendar-partial", response_class=HTMLResponse)
@db_session
def calendar_partial(
    request: Request,
    year: int = Query(...),
    month: int = Query(...)
):
    """Liefert das Kalender-Partial für einen bestimmten Monat."""
    # Kalenderdaten erstellen
    calendar_weeks = get_calendar_data(year, month)
    
    # Termine für den Monat laden
    start_date = calendar_weeks[0][0]["date"]
    end_date = calendar_weeks[-1][-1]["date"]
    
    # Termine aus der Datenbank laden
    appointments = list(DBAppointment.select(
        lambda a: a.date >= start_date and a.date <= end_date
    ))
    
    # Termine in den Kalender einfügen
    for appointment in appointments:
        # Pydantic-Schema erstellen und end_time_str hinzufügen
        appointment_data = schemas.Appointment.model_validate(appointment)
        
        # In ein Wörterbuch konvertieren für die Verarbeitung im Template
        try:
            # Pydantic v2 verwendet model_dump() statt dict()
            appointment_data_dict = appointment_data.model_dump()
        except AttributeError:
            # Fallback für ältere Pydantic-Versionen
            appointment_data_dict = appointment_data.dict()
        
        # get_end_time_str Methode zum Dictionary hinzufügen
        appointment_data_dict["get_end_time_str"] = appointment_data.get_end_time_str
        
        # Datum des Termins
        appointment_date = appointment_data.date
        
        # Termin dem entsprechenden Tag zuordnen
        for week in calendar_weeks:
            for day in week:
                if day["date"] == appointment_date:
                    day["appointments"].append(appointment_data_dict)
    
    # Template rendern
    return templates.TemplateResponse(
        "calendar_partial.html",
        {
            "request": request,
            "calendar_weeks": calendar_weeks
        }
    )


@router.get("/plans", response_class=HTMLResponse)
def plans(request: Request):
    """Seite mit Plänen."""
    return templates.TemplateResponse(
        "plans.html",
        {"request": request}
    )


@router.get("/locations", response_class=HTMLResponse)
def locations(request: Request):
    """Seite mit Arbeitsorten."""
    return templates.TemplateResponse(
        "locations.html",
        {"request": request}
    )
