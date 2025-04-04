from datetime import date, time, timedelta
from typing import List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Json, Field, ConfigDict


class BaseSchema(BaseModel):
    """Base class for all schemas."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class Address(BaseSchema):
    street: str
    postal_code: str
    city: str


class LocationOfWork(BaseSchema):
    name: str
    address: UUID


class LocationOfWorkDetail(BaseSchema):
    name: str
    address: Address


class Person(BaseSchema):
    name: str
    email: Optional[str] = None


class PlanPeriod(BaseSchema):
    name: str
    start_date: date
    end_date: date


class Appointment(BaseSchema):
    plan_period_id: UUID
    date: date
    start_time: time
    delta: timedelta
    location_id: UUID
    person_ids: List[UUID]
    guests: list[str] = Field(default_factory=list)
    notes: str = ""


class AppointmentDetail(BaseSchema):
    id: UUID
    plan_period: PlanPeriod
    date: date
    start_time: time
    delta: timedelta
    location: LocationOfWorkDetail
    persons: List[Person]
    guests: list[str] = Field(default_factory=list)
    notes: str = ""


class Plan(BaseSchema):
    name: str
    notes: str = ""
    plan_period_id: UUID
    appointment_ids: List[UUID]


class PlanDetail(BaseSchema):
    name: str
    notes: str = ""
    plan_period: PlanPeriod
    appointments: List[Appointment]
