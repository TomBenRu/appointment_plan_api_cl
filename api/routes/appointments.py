from datetime import date, timedelta, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query, Path, HTTPException, Depends
from pony.orm import db_session, select

from api.models import schemas
from database.models import Appointment as DBAppointment
from database.models import PlanPeriod as DBPlanPeriod
from database.models import LocationOfWork as DBLocationOfWork
from database.models import Person as DBPerson

router = APIRouter()


@router.get("/", response_model=List[schemas.Appointment])
@db_session
def get_appointments(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    location_id: Optional[UUID] = None,
    person_id: Optional[UUID] = None,
    plan_period_id: Optional[UUID] = None
):
    """
    Liefert eine Liste aller Termine, die den Filterkriterien entsprechen.
    """
    query = select(a for a in DBAppointment)
    
    if start_date:
        query = query.filter(lambda a: a.date >= start_date)
    
    if end_date:
        query = query.filter(lambda a: a.date <= end_date)
    
    if location_id:
        query = query.filter(lambda a: a.location.id == location_id)
    
    if person_id:
        query = query.filter(lambda a: person_id in [p.id for p in a.persons])
    
    if plan_period_id:
        query = query.filter(lambda a: a.plan_period.id == plan_period_id)
    
    appointments = list(query)
    return [schemas.Appointment.model_validate(a) for a in appointments]


@router.get("/{appointment_id}", response_model=schemas.AppointmentDetail)
@db_session
def get_appointment(appointment_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Termin.
    """
    appointment = DBAppointment.get(id=appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Termin nicht gefunden")
    
    return schemas.AppointmentDetail.model_validate(appointment)


@router.get("/by-date/{date_str}", response_model=List[schemas.Appointment])
@db_session
def get_appointments_by_date(date_str: str = Path(...)):
    """
    Liefert alle Termine für ein bestimmtes Datum.
    Das Datum sollte im Format YYYY-MM-DD sein.
    """
    try:
        appointment_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Ungültiges Datumsformat. Bitte verwenden Sie das Format YYYY-MM-DD."
        )
    
    appointments = list(DBAppointment.select(lambda a: a.date == appointment_date))
    return [schemas.Appointment.model_validate(a) for a in appointments]


@router.get("/by-month/{year}/{month}", response_model=List[schemas.Appointment])
@db_session
def get_appointments_by_month(year: int = Path(...), month: int = Path(...)):
    """
    Liefert alle Termine für einen bestimmten Monat.
    """
    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Monat. Der Monat muss zwischen 1 und 12 liegen."
        )
    
    # Bestimme den ersten und letzten Tag des Monats
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    start_date = date(year, month, 1)
    end_date = date(next_year, next_month, 1) - timedelta(days=1)
    
    appointments = list(DBAppointment.select(
        lambda a: a.date >= start_date and a.date <= end_date
    ))
    
    return [schemas.Appointment.model_validate(a) for a in appointments]
