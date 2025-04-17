from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Query, Path, HTTPException, Depends

from api.models import schemas
from api.services import AppointmentService

router = APIRouter()


@router.get("/", response_model=List[schemas.Appointment])
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
    # AppointmentService nutzen
    appointment_service = AppointmentService()
    return appointment_service.get_appointments(
        start_date=start_date,
        end_date=end_date,
        location_id=location_id,
        person_id=person_id,
        plan_period_id=plan_period_id
    )


@router.get("/{appointment_id}", response_model=schemas.AppointmentDetail)
def get_appointment(appointment_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Termin.
    """
    # AppointmentService nutzen
    appointment_service = AppointmentService()
    appointment = appointment_service.get_appointment_detail(appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Termin nicht gefunden")
    
    return appointment


@router.get("/by-date/{date_str}", response_model=List[schemas.Appointment])
def get_appointments_by_date(date_str: str = Path(...)):
    """
    Liefert alle Termine für ein bestimmtes Datum.
    Das Datum sollte im Format YYYY-MM-DD sein.
    """
    try:
        # Datumformat validieren
        date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Ungültiges Datumsformat. Bitte verwenden Sie das Format YYYY-MM-DD."
        )
    
    # AppointmentService nutzen
    appointment_service = AppointmentService()
    return appointment_service.get_appointments_by_date(date_str)


@router.get("/by-month/{year}/{month}", response_model=List[schemas.Appointment])
def get_appointments_by_month(year: int = Path(...), month: int = Path(...)):
    """
    Liefert alle Termine für einen bestimmten Monat.
    """
    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Monat. Der Monat muss zwischen 1 und 12 liegen."
        )
    
    # AppointmentService nutzen
    appointment_service = AppointmentService()
    return appointment_service.get_appointments_by_month(year, month)
