from datetime import datetime, date, time, timedelta
from typing import List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Json, Field, field_validator, ConfigDict


class BaseSchema(BaseModel):
    """Basis-Schema für alle Modelle"""
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
    f_name: str
    l_name: str
    email: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f'{self.f_name} {self.l_name}'


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
    
    def get_end_time(self) -> time:
        """Gibt die Endzeit als time-Objekt zurück"""
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + self.delta
        return end_datetime.time()
    
    @property
    def end_time_str(self) -> str:
        """Gibt die Endzeit als String in HH:MM Format zurück"""
        return self.get_end_time().strftime("%H:%M")

    @property
    def start_time_str(self) -> str:
        """Gibt die Startzeit als String in HH:MM Format zurück"""
        return self.start_time.strftime("%H:%M")


class AppointmentDetail(BaseSchema):
    plan_period: PlanPeriod
    date: date
    start_time: time
    delta: timedelta
    location: LocationOfWorkDetail
    persons: List[Person]
    guests: list[str] = Field(default_factory=list)
    notes: str = ""

    def get_end_time(self) -> time:
        """Gibt die Endzeit als time-Objekt zurück"""
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + self.delta
        return end_datetime.time()

    @property
    def date_str(self) -> str:
        """Gibt das Datum als String im Format DD.MM.YYYY zurück"""
        return self.date.strftime("%d.%m.%Y")

    @property
    def end_time_str(self) -> str:
        """Gibt die Endzeit als String in HH:MM Format zurück"""
        return self.get_end_time().strftime("%H:%M")

    @property
    def start_time_str(self) -> str:
        """Gibt die Startzeit als String in HH:MM Format zurück"""
        return self.start_time.strftime("%H:%M")

    @field_validator('persons', 'guests')
    def set_to_list(cls, v):
        return list(v)


class Plan(BaseSchema):
    name: str
    notes: str = ""
    plan_period_id: UUID
    appointment_ids: List[UUID]


class PlanDetail(BaseSchema):
    name: str
    notes: str = ""
    plan_period: PlanPeriod
    appointments: List[AppointmentDetail]

    @field_validator('appointments')
    def set_to_list(cls, v):
        return list(v)
