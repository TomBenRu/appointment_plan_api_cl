import calendar
from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID

from pony.orm import db_session, select

from api.models import schemas
from database.models import Appointment as DBAppointment
from database.models import Person as DBPerson
from database.models import LocationOfWork as DBLocationOfWork


class CalendarService:
    @staticmethod
    def get_month_name(month: int) -> str:
        """Gibt den deutschen Monatsnamen zurück."""
        return {
            1: "Januar", 2: "Februar", 3: "März", 
            4: "April", 5: "Mai", 6: "Juni",
            7: "Juli", 8: "August", 9: "September", 
            10: "Oktober", 11: "November", 12: "Dezember"
        }[month]
    
    @staticmethod
    def get_calendar_data(year: int, month: int) -> List[List[Dict[str, Any]]]:
        """Erstellt die Kalenderdaten für den angegebenen Monat."""
        # Kalenderobjekt erstellen (Woche beginnt mit Montag)
        cal = calendar.Calendar(firstweekday=0)
        
        # Heutiges Datum
        today = date.today()
        
        # Alle Tage des Monats inkl. angrenzender Tage bekommen
        month_days = cal.monthdatescalendar(year, month)
        
        # Ergebnisliste vorbereiten
        calendar_weeks = []
        
        # Alle Tage des Monats mit Terminen befüllen
        for week in month_days:
            week_data = []
            for day in week:
                day_data = {
                    "date": day,
                    "day": day.day,
                    "is_current_month": day.month == month,
                    "is_today": day == today,
                    "appointments": []  # Wird später befüllt
                }
                week_data.append(day_data)
            calendar_weeks.append(week_data)
        
        return calendar_weeks
    
    @staticmethod
    @db_session
    def fill_calendar_with_appointments(
        calendar_weeks: List[List[Dict[str, Any]]],
        filter_person_id: Optional[str] = None,
        filter_location_id: Optional[str] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Füllt den Kalender mit Terminen aus der Datenbank und wendet optionale Filter an.
        """
        # Termine für den aktuellen Monat laden
        start_date = calendar_weeks[0][0]["date"]  # Erster Tag im Kalender
        end_date = calendar_weeks[-1][-1]["date"]  # Letzter Tag im Kalender
        
        # Basisabfrage
        appointments_query = DBAppointment.select(
            lambda a: a.date >= start_date and a.date <= end_date
        )
        
        # Filterung nach Person
        if filter_person_id:
            try:
                person_uuid = UUID(filter_person_id) if isinstance(filter_person_id, str) else filter_person_id
                person = DBPerson.get(id=person_uuid)
                if person:
                    appointments_query = select(a for a in appointments_query if person in a.persons)
            except (ValueError, TypeError):
                pass  # Ungültige UUID ignorieren
        
        # Filterung nach Arbeitsort
        if filter_location_id:
            try:
                location_uuid = UUID(filter_location_id) if isinstance(filter_location_id, str) else filter_location_id
                appointments_query = appointments_query.filter(
                    lambda a: a.location.id == location_uuid
                )
            except (ValueError, TypeError):
                pass  # Ungültige UUID ignorieren
        
        # Abfrage ausführen
        appointments = list(appointments_query)
        
        # Termine in den Kalender einfügen
        for appointment in appointments:
            appointment_data = schemas.AppointmentDetail.model_validate(appointment)
            
            # Termin dem entsprechenden Tag zuordnen
            for week in calendar_weeks:
                for day in week:
                    if day["date"] == appointment.date:
                        day["appointments"].append(appointment_data)
        
        # Termine nach Startzeit sortieren
        for week in calendar_weeks:
            for day in week:
                day["appointments"].sort(key=lambda a: (a.start_time, a.delta))
        
        return calendar_weeks
    
    @staticmethod
    @db_session
    def get_active_filters(
        filter_person_id: Optional[str] = None,
        filter_location_id: Optional[str] = None
    ) -> Dict[str, Optional[Dict[str, str]]]:
        """
        Gibt aktive Filter für die Anzeige im Kalender zurück.
        """
        active_filters = {
            "person": None,
            "location": None
        }
        
        # Namen der gefilterten Entitäten abrufen für die Anzeige
        if filter_person_id:
            try:
                person_uuid = UUID(filter_person_id) if isinstance(filter_person_id, str) else filter_person_id
                person = DBPerson.get(id=person_uuid)
                if person:
                    active_filters["person"] = {"id": str(person.id), "name": f"{person.f_name} {person.l_name}"}
            except (ValueError, TypeError):
                pass  # Ungültige UUID ignorieren
        
        if filter_location_id:
            try:
                location_uuid = UUID(filter_location_id) if isinstance(filter_location_id, str) else filter_location_id
                location = DBLocationOfWork.get(id=location_uuid)
                if location:
                    active_filters["location"] = {"id": str(location.id), "name": location.name}
            except (ValueError, TypeError):
                pass  # Ungültige UUID ignorieren
        
        return active_filters
    
    @staticmethod
    @db_session
    def get_filter_options() -> Dict[str, List[Any]]:
        """
        Lädt alle Filter-Optionen (Personen und Arbeitsorte) für die Kalenderansicht.
        """
        # Alle Personen und Arbeitsorte für Filter-Dropdowns laden
        all_persons = [schemas.Person.model_validate(p) for p in 
                       DBPerson.select().order_by(lambda p: (p.l_name, p.f_name))]
        all_locations = [schemas.LocationOfWorkDetail.model_validate(l) for l in 
                         DBLocationOfWork.select().order_by(lambda l: l.name)]
        
        return {
            "all_persons": all_persons,
            "all_locations": all_locations
        }
    
    @staticmethod
    def adjust_month(year: int, month: int, direction: Optional[str] = None) -> Dict[str, int]:
        """
        Passt Jahr und Monat basierend auf der angegebenen Richtung an.
        """
        if direction == "today":
            today = date.today()
            return {"year": today.year, "month": today.month}
        elif direction == "prev":
            if month == 1:
                return {"year": year - 1, "month": 12}
            else:
                return {"year": year, "month": month - 1}
        elif direction == "next":
            if month == 12:
                return {"year": year + 1, "month": 1}
            else:
                return {"year": year, "month": month + 1}
        else:
            return {"year": year, "month": month}
    
    @staticmethod
    @db_session
    def get_day_view_data(date_str: str) -> Dict[str, Any]:
        """
        Bereitet Daten für die Tagesansicht vor.
        """
        try:
            selected_date = date.fromisoformat(date_str)
        except ValueError:
            return {
                "error": "Ungültiges Datumsformat. Bitte verwenden Sie das Format YYYY-MM-DD."
            }
        
        # Termine für den ausgewählten Tag laden
        appointments = list(DBAppointment.select(lambda a: a.date == selected_date).order_by(lambda a: a.start_time))
        appointments_data = [schemas.AppointmentDetail.model_validate(a) for a in appointments]
        
        # Formatierte Datumsangaben
        day_name = selected_date.strftime("%A")
        # Deutsche Wochentagsnamen
        day_names = {
            "Monday": "Montag",
            "Tuesday": "Dienstag",
            "Wednesday": "Mittwoch",
            "Thursday": "Donnerstag",
            "Friday": "Freitag",
            "Saturday": "Samstag",
            "Sunday": "Sonntag"
        }
        day_name = day_names.get(day_name, day_name)
        
        formatted_date = selected_date.strftime("%d.%m.%Y")
        
        return {
            "date": selected_date,
            "day_name": day_name,
            "formatted_date": formatted_date,
            "appointments": appointments_data,
            "is_today": selected_date == date.today()
        }
