from datetime import date, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from pony.orm import db_session, select, desc, exists

from api.models import schemas
from database.models import Appointment as DBAppointment
from database.models import Person as DBPerson
from database.models import LocationOfWork as DBLocationOfWork


class AppointmentService:
    @staticmethod
    @db_session
    def get_appointment_detail(appointment_id: UUID) -> Optional[schemas.AppointmentDetail]:
        """
        Liefert Details zu einem bestimmten Termin.
        """
        appointment = DBAppointment.get(id=appointment_id)
        if not appointment:
            return None
        
        return schemas.AppointmentDetail.model_validate(appointment)
    
    @staticmethod
    @db_session
    def get_appointments(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        location_id: Optional[UUID] = None,
        person_id: Optional[UUID] = None,
        plan_period_id: Optional[UUID] = None
    ) -> List[schemas.Appointment]:
        """
        Liefert eine Liste aller Termine, die den Filterkriterien entsprechen.
        """
        query = select(a for a in DBAppointment)
        
        if start_date:
            query = query.filter(lambda a: a.date >= start_date)
        
        if end_date:
            query = query.filter(lambda a: a.date <= end_date)
        
        if location_id:
            query = query.filter(lambda a: a.location.id == location_id)
        
        if person_id:
            person = DBPerson.get(id=person_id)
            if person:
                query = query.filter(lambda a: person in a.persons)
        
        if plan_period_id:
            query = query.filter(lambda a: a.plan_period.id == plan_period_id)
        
        appointments = list(query)
        return [schemas.Appointment.model_validate(a) for a in appointments]
        
    @staticmethod
    @db_session
    def get_appointments_by_date(date_str: str) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle Termine für ein bestimmtes Datum.
        Das Datum sollte im Format YYYY-MM-DD sein.
        """
        try:
            appointment_date = date.fromisoformat(date_str)
        except ValueError:
            return []
        
        appointments = list(DBAppointment.select(lambda a: a.date == appointment_date).order_by(lambda a: a.start_time))
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_appointments_by_month(year: int, month: int) -> List[schemas.Appointment]:
        """
        Liefert alle Termine für einen bestimmten Monat.
        """
        if not (1 <= month <= 12):
            return []
        
        # Bestimme den ersten und letzten Tag des Monats
        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        
        start_date = date(year, month, 1)
        end_date = date(next_year, next_month, 1) - timedelta(days=1)
        
        appointments = list(DBAppointment.select(
            lambda a: a.date >= start_date and a.date <= end_date
        ))
        
        return [schemas.Appointment.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_future_appointments_for_person(person_id: UUID) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle zukünftigen Termine für eine bestimmte Person.
        """
        today = date.today()
        person = DBPerson.get(id=person_id)
        if not person:
            return []
            
        appointments = DBAppointment.select(
            lambda a: person in a.persons and a.date >= today
        ).order_by(lambda a: (a.date, a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_past_appointments_for_person(person_id: UUID, days: int = 30) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle vergangenen Termine für eine bestimmte Person innerhalb der letzten X Tage.
        """
        today = date.today()
        past_date = today - timedelta(days=days)
        person = DBPerson.get(id=person_id)
        if not person:
            return []
            
        appointments = DBAppointment.select(
            lambda a: person in a.persons and a.date < today and a.date >= past_date
        ).order_by(lambda a: (desc(a.date), a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_future_appointments_for_location(location_id: UUID) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle zukünftigen Termine für einen bestimmten Ort.
        """
        today = date.today()
        location = DBLocationOfWork.get(id=location_id)
        if not location:
            return []
            
        appointments = DBAppointment.select(
            lambda a: a.location.id == location_id and a.date >= today
        ).order_by(lambda a: (a.date, a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_past_appointments_for_location(location_id: UUID, days: int = 30) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle vergangenen Termine für einen bestimmten Ort innerhalb der letzten X Tage.
        """
        today = date.today()
        past_date = today - timedelta(days=days)
        location = DBLocationOfWork.get(id=location_id)
        if not location:
            return []
            
        appointments = DBAppointment.select(
            lambda a: a.location.id == location_id and a.date < today and a.date >= past_date
        ).order_by(lambda a: (desc(a.date), a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def search_appointments(search_term: str, limit: int = 20) -> List[schemas.AppointmentDetail]:
        """
        Durchsucht Termine nach dem angegebenen Suchbegriff.
        """
        search_term_lower = search_term.lower()
        
        appointments = select(a for a in DBAppointment if
                           # 1. Suche in Notizen (case-insensitive, None-sicher)
                           (a.notes and search_term_lower in a.notes.lower()) or
                           
                           # 2. Suche in verknüpften Personen (case-insensitive)
                           exists(p for p in a.persons if
                                  (p.f_name and search_term_lower in p.f_name.lower()) or
                                  (p.l_name and search_term_lower in p.l_name.lower())
                           ) or
                           
                           # 3. Suche im Namen des Ortes (case-insensitive)
                           (a.location and a.location.name and search_term_lower in a.location.name.lower()) or
                           
                           # 4. Suche in Gästen
                           (search_term_lower in str(a.guests).lower())
        )
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments.order_by(lambda a: a.date)[:limit]]
