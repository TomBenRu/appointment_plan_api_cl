"""
Dieses Skript fügt Testdaten in die Datenbank ein.
Ausführen mit: python seed.py
"""

import datetime
import uuid
from datetime import date, timedelta
import json
import random

from pony.orm import db_session, commit

from database import setup_database
from database.models import Address, LocationOfWork, Person, PlanPeriod, Appointment, Plan, Team, Project


@db_session
def seed_database():
    """Fügt Testdaten in die Datenbank ein."""
    print("Füge Testdaten hinzu...")
    
    # Adressen erstellen
    print("Erstelle Adressen...")
    addresses = [
        Address(
            street="Hauptstraße 1",
            postal_code="10115",
            city="Berlin"
        ),
        Address(
            street="Nebenweg 23",
            postal_code="20095",
            city="Hamburg"
        ),
        Address(
            street="Schlossallee 42",
            postal_code="80333",
            city="München"
        ),
        Address(
            street="Bahnhofstraße 7",
            postal_code="50667",
            city="Köln"
        ),
        Address(
            street="Marktplatz 12",
            postal_code="60311",
            city="Frankfurt"
        )
    ]
    
    # Arbeitsorte erstellen
    print("Erstelle Arbeitsorte...")
    locations = [
        LocationOfWork(
            name="Büro Berlin",
            address=addresses[0]
        ),
        LocationOfWork(
            name="Coworking Space Hamburg",
            address=addresses[1]
        ),
        LocationOfWork(
            name="Konferenzraum München",
            address=addresses[2]
        ),
        LocationOfWork(
            name="Besprechungsraum Köln",
            address=addresses[3]
        ),
        LocationOfWork(
            name="Home Office Frankfurt",
            address=addresses[4]
        )
    ]
    
    # Personen erstellen
    print("Erstelle Personen...")
    persons = [
        Person(
            f_name="Max",
            l_name="Mustermann",
            email="max.mustermann@example.com"
        ),
        Person(
            f_name="Erika",
            l_name="Musterfrau",
            email="erika.musterfrau@example.com"
        ),
        Person(
            f_name="John",
            l_name="Doe",
            email="john.doe@example.com"
        ),
        Person(
            f_name="Jane",
            l_name="Smith",
            email="jane.smith@example.com"
        ),
        Person(
            f_name="Hans",
            l_name="Schmidt",
            email="hans.schmidt@example.com"
        ),
        Person(
            f_name="Maria",
            l_name="Müller",
            email="maria.mueller@example.com"
        )
    ]
    
    # Teams erstellen
    print("Erstelle Teams...")
    teams = [
        Team(
            name="Baden-Württemberg",
            dispatcher=persons[0]  # Max als Dispatcher
        ),
        Team(
            name="Mainz",
            dispatcher=persons[1]  # Erika als Dispatcher
        )
    ]
    
    # Mitarbeiter zu Teams hinzufügen
    persons[2].team_of_employee = teams[0]  # John gehört zum Entwicklungsteam
    persons[4].team_of_employee = teams[0]  # Hans gehört zum Entwicklungsteam
    persons[3].team_of_employee = teams[1]  # Jane gehört zum Marketingteam
    persons[5].team_of_employee = teams[1]  # Maria gehört zum Marketingteam
    
    # Projekte erstellen
    print("Erstelle Projekte...")
    projects = [
        Project(
            name="Humor Hilft Heilen",
            active=True,
            admin=persons[0]  # Max als Admin
        ),
        Project(
            name="Clinic Clowns China",
            active=True,
            admin=persons[1]  # Erika als Admin
        ),
        Project(
            name="Health fror Humor",
            active=False,
            admin=persons[0]  # Max als Admin
        )
    ]
    
    # Personen zu Projekten hinzufügen
    projects[0].persons.add(persons[2])  # John arbeitet am Website Relaunch
    projects[0].persons.add(persons[3])  # Jane arbeitet am Website Relaunch
    projects[1].persons.add(persons[4])  # Hans arbeitet an der Mobile App
    projects[1].persons.add(persons[5])  # Maria arbeitet an der Mobile App
    projects[2].persons.add(persons[2])  # John arbeitet auch am Legacy System
    projects[2].persons.add(persons[4])  # Hans arbeitet auch am Legacy System
    
    # Planungsperioden erstellen
    print("Erstelle Planungsperioden...")
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Aktuelle Planungsperiode (aktueller Monat)
    current_period_start = date(current_year, current_month, 1)
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
        
    current_period_end = date(next_year, next_month, 1) - timedelta(days=1)
    
    # Nächste Planungsperiode (nächster Monat)
    next_period_start = date(next_year, next_month, 1)
    if next_month == 12:
        after_next_month = 1
        after_next_year = next_year + 1
    else:
        after_next_month = next_month + 1
        after_next_year = next_year
        
    next_period_end = date(after_next_year, after_next_month, 1) - timedelta(days=1)
    
    # Planungsperioden speichern
    plan_periods = [
        PlanPeriod(
            name=f"Planungsperiode {current_period_start.strftime('%B %Y')}",
            start_date=current_period_start,
            end_date=current_period_end
        ),
        PlanPeriod(
            name=f"Planungsperiode {next_period_start.strftime('%B %Y')}",
            start_date=next_period_start,
            end_date=next_period_end
        )
    ]
    
    # Teams mit Planungsperioden verknüpfen
    teams[0].plan_periods.add(plan_periods[0])
    teams[1].plan_periods.add(plan_periods[1])
    
    # Pläne erstellen
    print("Erstelle Pläne...")
    plans = [
        Plan(
            name="Plan Alpha",
            notes="Bitte pünktlich sein!",
            plan_period=plan_periods[0]
        ),
        Plan(
            name="Plan Beta",
            notes="Bitte alle Termine beachten.",
            plan_period=plan_periods[1]
        )
    ]
    
    # Termine für den aktuellen Monat erstellen
    print("Erstelle Termine...")
    
    # Liste von möglichen Startzeiten
    start_times = [datetime.time(9, 0), datetime.time(10, 30),
                   datetime.time(13, 0), datetime.time(14, 30), datetime.time(16, 0)]
    
    # Liste von möglichen Dauern (in Sekunden)
    durations = [datetime.timedelta(seconds=3600), datetime.timedelta(seconds=5400), datetime.timedelta(seconds=7200)]
    
    # Aktuelle Termine erstellen (für die aktuelle Planungsperiode)
    for i in range(15):  # 15 Termine für den aktuellen Monat
        # Zufälliges Datum innerhalb der aktuellen Planungsperiode
        days_in_period = (current_period_end - current_period_start).days + 1
        random_day = random.randint(0, days_in_period - 1)
        appointment_date = current_period_start + timedelta(days=random_day)
        
        # Wochenenden überspringen
        if appointment_date.weekday() >= 5:  # 5 = Samstag, 6 = Sonntag
            continue
        
        # Zufällige Startzeit und Dauer
        start_time: datetime.time = random.choice(start_times)
        duration: datetime.timedelta = random.choice(durations)
        
        # Zufällige Teilnehmer (1-3 Personen)
        num_participants = random.randint(1, 3)
        participants = random.sample(persons, num_participants)
        
        # Zufällige Gäste (0-2 Gäste)
        num_guests = random.randint(0, 2)
        guest_names = [f"Gast {j+1}" for j in range(num_guests)]
        
        # Zufälliger Arbeitsort
        location = random.choice(locations)
        
        # Termin erstellen
        appointment = Appointment(
            plan_period=plan_periods[0],
            date=appointment_date,
            start_time=start_time,
            delta=duration,
            location=location,
            notes=f"Termin am {appointment_date.strftime('%d.%m.%Y')} in {location.name}",
            guests=guest_names
        )
        
        # Teilnehmer hinzufügen
        for participant in participants:
            appointment.persons.add(participant)
        
        # Dem entsprechenden Plan hinzufügen
        plans[0].appointments.add(appointment)
    
    # Zukünftige Termine erstellen (für die nächste Planungsperiode)
    for i in range(10):  # 10 Termine für den nächsten Monat
        # Zufälliges Datum innerhalb der nächsten Planungsperiode
        days_in_period = (next_period_end - next_period_start).days + 1
        random_day = random.randint(0, days_in_period - 1)
        appointment_date = next_period_start + timedelta(days=random_day)
        
        # Wochenenden überspringen
        if appointment_date.weekday() >= 5:  # 5 = Samstag, 6 = Sonntag
            continue
        
        # Zufällige Startzeit und Dauer
        start_time = random.choice(start_times)
        duration = random.choice(durations)
        
        # Zufällige Teilnehmer (1-3 Personen)
        num_participants = random.randint(1, 3)
        participants = random.sample(persons, num_participants)
        
        # Zufällige Gäste (0-2 Gäste)
        num_guests = random.randint(0, 2)
        guest_names = [f"Gast {j+1}" for j in range(num_guests)]
        
        # Zufälliger Arbeitsort
        location = random.choice(locations)
        
        # Termin erstellen
        appointment = Appointment(
            plan_period=plan_periods[1],
            date=appointment_date,
            start_time=start_time,
            delta=duration,
            location=location,
            notes=f"Termin am {appointment_date.strftime('%d.%m.%Y')} in {location.name}",
            guests=guest_names
        )
        
        # Teilnehmer hinzufügen
        for participant in participants:
            appointment.persons.add(participant)
        
        # Dem entsprechenden Plan hinzufügen
        plans[1].appointments.add(appointment)
    
    commit()
    print("Testdaten erfolgreich eingefügt!")


if __name__ == "__main__":
    # Datenbank einrichten
    db = setup_database()
    
    # Testdaten einfügen
    seed_database()
