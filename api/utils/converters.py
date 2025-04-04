from datetime import time, timedelta
from uuid import UUID

from api.models import schemas


def address_to_schema(db_address):
    """Konvertiert ein Adress-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.Address(
        id=UUID(db_address.uuid),
        street=db_address.street,
        postal_code=db_address.postal_code,
        city=db_address.city
    )


def location_to_schema(db_location):
    """Konvertiert ein LocationOfWork-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.LocationOfWork(
        id=UUID(db_location.uuid),
        name=db_location.name,
        address=UUID(db_location.address.uuid)
    )


def location_to_detail_schema(db_location):
    """Konvertiert ein LocationOfWork-ORM-Objekt in ein DetailPydantic-Schema."""
    return schemas.LocationOfWorkDetail(
        id=UUID(db_location.uuid),
        name=db_location.name,
        address=address_to_schema(db_location.address)
    )


def person_to_schema(db_person):
    """Konvertiert ein Person-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.Person(
        id=UUID(db_person.uuid),
        name=db_person.name,
        email=db_person.email
    )


def plan_period_to_schema(db_plan_period):
    """Konvertiert ein PlanPeriod-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.PlanPeriod(
        id=UUID(db_plan_period.uuid),
        name=db_plan_period.name,
        start_date=db_plan_period.start_date,
        end_date=db_plan_period.end_date
    )


def appointment_to_schema(db_appointment):
    """Konvertiert ein Appointment-ORM-Objekt in ein Pydantic-Schema."""
    # Zeit-String in time-Objekt umwandeln
    start_time_parts = db_appointment.start_time.split(":")
    start_time_obj = time(
        hour=int(start_time_parts[0]),
        minute=int(start_time_parts[1]),
        second=int(start_time_parts[2]) if len(start_time_parts) > 2 else 0
    )
    
    return schemas.Appointment(
        id=UUID(db_appointment.uuid),
        plan_period_id=UUID(db_appointment.plan_period.uuid),
        date=db_appointment.date,
        start_time=start_time_obj,
        delta=timedelta(seconds=db_appointment.delta),
        location_id=UUID(db_appointment.location.uuid),
        person_ids=[UUID(p.uuid) for p in db_appointment.persons],
        guests=db_appointment.guests,
        notes=db_appointment.notes or ""
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
    
    return schemas.AppointmentDetail(
        id=UUID(db_appointment.uuid),
        plan_period=plan_period_to_schema(db_appointment.plan_period),
        date=db_appointment.date,
        start_time=start_time_obj,
        delta=timedelta(seconds=db_appointment.delta),
        location=location_to_detail_schema(db_appointment.location),
        persons=[person_to_schema(p) for p in db_appointment.persons],
        guests=db_appointment.guests,
        notes=db_appointment.notes or ""
    )


def plan_to_schema(db_plan):
    """Konvertiert ein Plan-ORM-Objekt in ein Pydantic-Schema."""
    return schemas.Plan(
        id=UUID(db_plan.uuid),
        name=db_plan.name,
        notes=db_plan.notes or "",
        plan_period_id=UUID(db_plan.plan_period.uuid),
        appointment_ids=[UUID(a.uuid) for a in db_plan.appointments]
    )


def plan_to_detail_schema(db_plan):
    """Konvertiert ein Plan-ORM-Objekt in ein DetailPydantic-Schema."""
    return schemas.PlanDetail(
        id=UUID(db_plan.uuid),
        name=db_plan.name,
        notes=db_plan.notes or "",
        plan_period=plan_period_to_schema(db_plan.plan_period),
        appointments=[appointment_to_schema(a) for a in db_plan.appointments]
    )
