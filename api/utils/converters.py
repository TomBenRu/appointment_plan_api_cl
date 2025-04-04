from datetime import time, timedelta, datetime, date
from uuid import UUID

from api.models import schemas


def address_to_schema(db_address):
    """Konvertiert ein Adress-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.Address(
        id=db_address.id,  # Bereits ein UUID-Objekt, keine Konvertierung notwendig
        street=db_address.street,
        postal_code=db_address.postal_code,
        city=db_address.city
    )


def location_to_schema(db_location):
    """Konvertiert ein LocationOfWork-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.LocationOfWork(
        id=db_location.id,
        name=db_location.name,
        address=db_location.address.id
    )


def location_to_detail_schema(db_location):
    """Konvertiert ein LocationOfWork-ORM-Objekt in ein DetailPydantic-Schema."""
    return schemas.LocationOfWorkDetail(
        id=db_location.id,
        name=db_location.name,
        address=address_to_schema(db_location.address)
    )


def person_to_schema(db_person):
    """Konvertiert ein Person-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.Person(
        id=db_person.id,
        name=db_person.name,
        email=db_person.email
    )


def plan_period_to_schema(db_plan_period):
    """Konvertiert ein PlanPeriod-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.PlanPeriod(
        id=db_plan_period.id,
        name=db_plan_period.name,
        start_date=db_plan_period.start_date,
        end_date=db_plan_period.end_date
    )


def calculate_end_time(start_time_obj, delta_seconds):
    """Berechnet die Endzeit basierend auf Startzeit und Dauer."""
    # Wir verwenden ein fiktives Datum, um die Zeit-Arithmetik zu ermöglichen
    dummy_date = date(2000, 1, 1)
    # Erstellen eines datetime-Objekts mit dem fiktiven Datum und der Startzeit
    start_datetime = datetime.combine(dummy_date, start_time_obj)
    # Addieren der Dauer
    end_datetime = start_datetime + timedelta(seconds=delta_seconds)
    # Extrahieren der Endzeit
    return end_datetime.time()


def appointment_to_schema(db_appointment):
    """Konvertiert ein Appointment-ORM-Objekt in ein Pydantic-Schema."""
    # Zeit-String in time-Objekt umwandeln
    start_time_parts = db_appointment.start_time.split(":")
    start_time_obj = time(
        hour=int(start_time_parts[0]),
        minute=int(start_time_parts[1]),
        second=int(start_time_parts[2]) if len(start_time_parts) > 2 else 0
    )
    
    # Endzeit berechnen
    end_time_obj = calculate_end_time(start_time_obj, db_appointment.delta)
    
    return schemas.Appointment(
        id=db_appointment.id,
        plan_period_id=db_appointment.plan_period.id,
        date=db_appointment.date,
        start_time=start_time_obj,
        delta=timedelta(seconds=db_appointment.delta),
        location_id=db_appointment.location.id,
        person_ids=[p.id for p in db_appointment.persons],
        guests=db_appointment.guests,
        notes=db_appointment.notes or "",
        end_time=end_time_obj  # Neue Eigenschaft hinzugefügt
    )


def appointment_to_detail_schema(db_appointment):
    """Konvertiert ein Appointment-ORM-Objekt in ein DetailPydantic-Schema."""
    # Zeit-String in time-Objekt umwandeln
    start_time_parts = db_appointment.start_time.split(":")
    start_time_obj = time(
        hour=int(start_time_parts[0]),
        minute=int(start_time_parts[1]),
        second=int(start_time_parts[2]) if len(start_time_parts) > 2 else 0
    )
    
    # Endzeit berechnen
    end_time_obj = calculate_end_time(start_time_obj, db_appointment.delta)
    
    return schemas.AppointmentDetail(
        id=db_appointment.id,
        plan_period=plan_period_to_schema(db_appointment.plan_period),
        date=db_appointment.date,
        start_time=start_time_obj,
        delta=timedelta(seconds=db_appointment.delta),
        location=location_to_detail_schema(db_appointment.location),
        persons=[person_to_schema(p) for p in db_appointment.persons],
        guests=db_appointment.guests,
        notes=db_appointment.notes or "",
        end_time=end_time_obj  # Neue Eigenschaft hinzugefügt
    )


def plan_to_schema(db_plan):
    """Konvertiert ein Plan-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.Plan(
        id=db_plan.id,
        name=db_plan.name,
        notes=db_plan.notes or "",
        plan_period_id=db_plan.plan_period.id,
        appointment_ids=[a.id for a in db_plan.appointments]
    )


def plan_to_detail_schema(db_plan):
    """Konvertiert ein Plan-ORM-Objekt in ein DetailPydantic-Schema."""
    return schemas.PlanDetail(
        id=db_plan.id,
        name=db_plan.name,
        notes=db_plan.notes or "",
        plan_period=plan_period_to_schema(db_plan.plan_period),
        appointments=[appointment_to_schema(a) for a in db_plan.appointments]
    )
