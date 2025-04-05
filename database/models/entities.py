import datetime
from datetime import date, time, timedelta
from uuid import UUID
import json
from typing import Optional, List

from pony.orm import Database, Required, Optional as PonyOptional, Set, Json, PrimaryKey

db = Database()

class Address(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    street = Required(str)
    postal_code = Required(str)
    city = Required(str)
    locations = Set('LocationOfWork')

class LocationOfWork(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str)
    address = Required(Address)
    appointments = Set('Appointment')

class Person(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    f_name = Required(str)
    l_name = Required(str)
    email = PonyOptional(str)
    appointments = Set('Appointment')

class PlanPeriod(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str)
    start_date = Required(date)
    end_date = Required(date)
    plans = Set('Plan')
    appointments = Set('Appointment')

class Appointment(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    plan_period = Required(PlanPeriod)
    date = Required(date)
    start_time = Required(datetime.time)  # Speichere als String im Format "HH:MM:SS"
    delta = Required(datetime.timedelta)  # Speichere als Sekunden
    location = Required(LocationOfWork)
    persons = Set(Person)
    guests = Required(Json, default=[])
    notes = PonyOptional(str)
    plans = Set('Plan')

class Plan(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str)
    notes = PonyOptional(str, default="")
    plan_period = Required(PlanPeriod)
    appointments = Set(Appointment)
