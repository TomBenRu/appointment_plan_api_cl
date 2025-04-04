from datetime import datetime, date, time, timedelta
from typing import List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Json, Field


class Address(BaseModel):
    id: UUID
    street: str
    postal_code: str
    city: str


class LocationOfWork(BaseModel):
    id: UUID
    name: str
    address: UUID


class LocationOfWorkDetail(BaseModel):
    id: UUID
    name: str
    address: Address


class Person(BaseModel):
    id: UUID
    name: str
    email: Optional[str] = None


class PlanPeriod(BaseModel):
    id: UUID
    name: str
    start_date: date
    end_date: date


class Appointment(BaseModel):
    id: UUID
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
    
    def get_end_time_str(self) -> str:
        """Gibt die Endzeit als String in HH:MM Format zurück"""
        return self.get_end_time().strftime("%H:%M")


class AppointmentDetail(BaseModel):
    id: UUID
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

    def get_end_time_str(self) -> str:
        """Gibt die Endzeit als String in HH:MM Format zurück"""
        return self.get_end_time().strftime("%H:%M")


class Plan(BaseModel):
    id: UUID
    name: str
    notes: str = ""
    plan_period_id: UUID
    appointment_ids: List[UUID]


class PlanDetail(BaseModel):
    id: UUID
    name: str
    notes: str = ""
    plan_period: PlanPeriod
    appointments: List[Appointment]
