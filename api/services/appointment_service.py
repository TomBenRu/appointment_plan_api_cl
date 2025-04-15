"""
Service für Termine mit integrierter Fehlerbehandlung.
"""
from datetime import date, timedelta, time as datetime_time
from typing import List, Optional, Dict, Any
from uuid import UUID

from pony.orm import db_session, select, desc, exists, ObjectNotFound

from api.models import schemas
from database.models import Appointment as DBAppointment
from database.models import Person as DBPerson
from database.models import LocationOfWork as DBLocationOfWork
from api.exceptions.appointment import (
    AppointmentNotFoundException, AppointmentOverlapException,
    InvalidAppointmentDateException, AppointmentUpdateConflictException
)
from api.exceptions.person import PersonNotFoundException
from api.exceptions.location import LocationNotFoundException


class AppointmentService:
    @staticmethod
    @db_session
    def get_appointment_detail(appointment_id: UUID) -> schemas.AppointmentDetail:
        """
        Liefert Details zu einem bestimmten Termin.
        Args: appointment_id: Die UUID des gesuchten Termins
        Returns: Details zum Termin
        Raises: AppointmentNotFoundException: Wenn der Termin nicht gefunden wurde
        """
        appointment = DBAppointment.get(id=appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(appointment_id=appointment_id)

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
        
        Args:
            start_date: Optional. Nur Termine ab diesem Datum
            end_date: Optional. Nur Termine bis zu diesem Datum
            location_id: Optional. Nur Termine an diesem Ort
            person_id: Optional. Nur Termine mit dieser Person
            plan_period_id: Optional. Nur Termine in dieser Planperiode
            
        Returns:
            Liste der gefilterten Termine
            
        Raises:
            LocationNotFoundException: Wenn ein nicht existierender Ort angegeben wurde
            PersonNotFoundException: Wenn eine nicht existierende Person angegeben wurde
        """
        query = select(a for a in DBAppointment)
        
        if start_date:
            query = query.filter(lambda a: a.date >= start_date)
        
        if end_date:
            query = query.filter(lambda a: a.date <= end_date)
        
        if location_id:
            location = DBLocationOfWork.get(id=location_id)
            if not location:
                raise LocationNotFoundException(location_id=location_id)
            query = query.filter(lambda a: a.location.id == location_id)
        
        if person_id:
            person = DBPerson.get(id=person_id)
            if not person:
                raise PersonNotFoundException(person_id=person_id)
            query = query.filter(lambda a: person in a.persons)
        
        if plan_period_id:
            query = query.filter(lambda a: a.plan_period.id == plan_period_id)

        return [schemas.Appointment.model_validate(a) for a in query]
        
    @staticmethod
    @db_session
    def get_appointments_by_date(date_str: str) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle Termine für ein bestimmtes Datum.
        
        Args:
            date_str: Das Datum im Format YYYY-MM-DD
            
        Returns:
            Liste der Termine an diesem Tag
            
        Raises:
            InvalidAppointmentDateException: Wenn das Datumsformat ungültig ist
        """
        try:
            appointment_date = date.fromisoformat(date_str)
        except ValueError:
            raise InvalidAppointmentDateException(
                message=f"Ungültiges Datumsformat: '{date_str}'. Erwartet wird YYYY-MM-DD.",
                field="date",
                value=date_str
            )
        
        appointments = DBAppointment.select(lambda a: a.date == appointment_date).order_by(lambda a: a.start_time)
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_appointments_by_month(year: int, month: int) -> List[schemas.Appointment]:
        """
        Liefert alle Termine für einen bestimmten Monat.
        
        Args:
            year: Das Jahr
            month: Der Monat (1-12)
            
        Returns:
            Liste der Termine in diesem Monat
            
        Raises:
            InvalidAppointmentDateException: Wenn Monat oder Jahr ungültig sind
        """
        if not (1 <= month <= 12):
            raise InvalidAppointmentDateException(
                message=f"Ungültiger Monat: {month}. Muss zwischen 1 und 12 liegen.",
                field="month",
                value=month
            )
        
        # Bestimme den ersten und letzten Tag des Monats
        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        
        try:
            start_date = date(year, month, 1)
            end_date = date(next_year, next_month, 1) - timedelta(days=1)
        except ValueError as e:
            raise InvalidAppointmentDateException(
                message=f"Ungültiges Datum: Jahr={year}, Monat={month}. {str(e)}",
                field="date",
                value=f"{year}-{month}"
            )
        
        appointments = DBAppointment.select( lambda a: a.date >= start_date and a.date <= end_date)
        
        return [schemas.Appointment.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_future_appointments_for_person(person_id: UUID) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle zukünftigen Termine für eine bestimmte Person.
        
        Args:
            person_id: Die UUID der Person
            
        Returns:
            Liste der zukünftigen Termine der Person
            
        Raises:
            PersonNotFoundException: Wenn die Person nicht gefunden wurde
        """
        today = date.today()
        person = DBPerson.get(id=person_id)
        if not person:
            raise PersonNotFoundException(person_id=person_id)
            
        appointments = DBAppointment.select(
            lambda a: person in a.persons and a.date >= today
        ).order_by(lambda a: (a.date, a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_past_appointments_for_person(person_id: UUID, days: int = 30) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle vergangenen Termine für eine bestimmte Person innerhalb der letzten X Tage.
        
        Args:
            person_id: Die UUID der Person
            days: Anzahl der Tage in der Vergangenheit (Standard: 30)
            
        Returns:
            Liste der vergangenen Termine der Person
            
        Raises:
            PersonNotFoundException: Wenn die Person nicht gefunden wurde
            InvalidAppointmentDateException: Wenn days ungültig ist
        """
        if days < 0:
            raise InvalidAppointmentDateException(
                message=f"Ungültige Tagesanzahl: {days}. Muss positiv sein.",
                field="days",
                value=days
            )
            
        today = date.today()
        past_date = today - timedelta(days=days)
        person = DBPerson.get(id=person_id)
        if not person:
            raise PersonNotFoundException(person_id=person_id)
            
        appointments = DBAppointment.select(
            lambda a: person in a.persons and a.date < today and a.date >= past_date
        ).order_by(lambda a: (desc(a.date), a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_future_appointments_for_location(location_id: UUID) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle zukünftigen Termine für einen bestimmten Ort.
        
        Args:
            location_id: Die UUID des Arbeitsortes
            
        Returns:
            Liste der zukünftigen Termine an diesem Ort
            
        Raises:
            LocationNotFoundException: Wenn der Ort nicht gefunden wurde
        """
        today = date.today()
        location = DBLocationOfWork.get(id=location_id)
        if not location:
            raise LocationNotFoundException(location_id=location_id)
            
        appointments = DBAppointment.select(
            lambda a: a.location.id == location_id and a.date >= today
        ).order_by(lambda a: (a.date, a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def get_past_appointments_for_location(location_id: UUID, days: int = 30) -> List[schemas.AppointmentDetail]:
        """
        Liefert alle vergangenen Termine für einen bestimmten Ort innerhalb der letzten X Tage.
        
        Args:
            location_id: Die UUID des Arbeitsortes
            days: Anzahl der Tage in der Vergangenheit (Standard: 30)
            
        Returns:
            Liste der vergangenen Termine an diesem Ort
            
        Raises:
            LocationNotFoundException: Wenn der Ort nicht gefunden wurde
            InvalidAppointmentDateException: Wenn days ungültig ist
        """
        if days < 0:
            raise InvalidAppointmentDateException(
                message=f"Ungültige Tagesanzahl: {days}. Muss positiv sein.",
                field="days",
                value=days
            )
            
        today = date.today()
        past_date = today - timedelta(days=days)
        location = DBLocationOfWork.get(id=location_id)
        if not location:
            raise LocationNotFoundException(location_id=location_id)
            
        appointments = DBAppointment.select(
            lambda a: a.location.id == location_id and a.date < today and a.date >= past_date
        ).order_by(lambda a: (desc(a.date), a.start_time))
        
        return [schemas.AppointmentDetail.model_validate(a) for a in appointments]
    
    @staticmethod
    @db_session
    def search_appointments(search_term: str, limit: int = 20) -> List[schemas.AppointmentDetail]:
        """
        Durchsucht Termine nach dem angegebenen Suchbegriff.
        
        Args:
            search_term: Der Suchbegriff
            limit: Maximale Anzahl der Ergebnisse (Standard: 20)
            
        Returns:
            Liste der passenden Termine
        """
        if not search_term or len(search_term.strip()) < 2:
            return []
            
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
        
    @staticmethod
    @db_session
    def check_appointment_overlap(
        appointment_date: date,
        start_time: datetime_time,
        end_time: datetime_time,
        location_id: UUID,
        exclude_appointment_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Prüft, ob es Überschneidungen mit anderen Terminen gibt.
        
        Args:
            appointment_date: Das Datum des Termins
            start_time: Die Startzeit
            end_time: Die Endzeit
            location_id: Die ID des Arbeitsortes
            exclude_appointment_id: Optional. ID eines Termins, der bei der Prüfung ignoriert werden soll
            
        Returns:
            Liste mit Informationen zu überlappenden Terminen (leer, wenn keine Überschneidungen)
        """
        # Aufbau der Basis-Query
        query = DBAppointment.select(lambda a: 
            a.date == appointment_date and 
            a.location.id == location_id
        )
        
        # Ausschluss des aktuellen Termins bei Aktualisierungen
        if exclude_appointment_id:
            query = query.filter(lambda a: a.id != exclude_appointment_id)
        
        # Alle potenziell überlappenden Termine finden
        appointments = list(query)
        
        # Prüfen, ob Überschneidungen existieren
        overlapping = []
        
        for appt in appointments:
            appt_end_time = (datetime_time.fromisoformat(str(appt.start_time)) + 
                             appt.delta)
            
            # Überschneidungsprüfung: 
            # (StartA <= EndB) und (EndA >= StartB)
            if (start_time <= appt_end_time and 
                end_time >= appt.start_time):
                
                # Informationen zum überlappenden Termin sammeln
                overlapping.append({
                    "id": str(appt.id),
                    "date": str(appt.date),
                    "start_time": str(appt.start_time),
                    "end_time": str(appt_end_time),
                    "location": appt.location.name
                })
        
        return overlapping
