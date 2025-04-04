import calendar
import pprint
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, Query, HTTPException
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
