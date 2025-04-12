import datetime
from datetime import date, time, timedelta
from uuid import UUID

from pony.orm import Required, Optional as PonyOptional, Set, Json, PrimaryKey

from .base import db

def utcnow_naive():
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

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
    project = PonyOptional('Project')
    team_of_employee = PonyOptional('Team')
    teams_of_dispatcher = Set('Team')
    project_of_admin = PonyOptional('Project', reverse='admin')
    appointments = Set('Appointment')
    auth_user = PonyOptional('User')

class PlanPeriod(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str)
    start_date = Required(date)
    end_date = Required(date)
    plan = PonyOptional('Plan')
    appointments = Set('Appointment')
    teams = Set('Team')

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

class Team(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str, 50)
    employees = Set(Person, reverse='team_of_employee')
    dispatcher = Required(Person, reverse='teams_of_dispatcher')
    plan_periods = Set(PlanPeriod)

class Project(db.Entity):
    id = PrimaryKey(UUID, auto=True)
    name = Required(str, 50, unique=True)
    active = Required(bool, default=False)
    persons = Set('Person', reverse='project')
    admin = PonyOptional('Person', reverse='project_of_admin')
