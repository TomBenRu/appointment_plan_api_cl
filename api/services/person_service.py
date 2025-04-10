"""
Service für Personen mit integrierter Fehlerbehandlung.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID

from pony.orm import db_session, select, count, ObjectNotFound

from api.models import schemas
from database.models import Person as DBPerson
from api.exceptions.person import (
    PersonNotFoundException, PersonInUseException,
    DuplicatePersonException, PersonValidationException
)


class PersonService:
    @staticmethod
    @db_session
    def get_all_persons() -> List[schemas.Person]:
        """
        Liefert eine Liste aller Personen.
        
        Returns:
            Eine Liste aller Personen.
        """
        persons = list(DBPerson.select().order_by(lambda p: (p.l_name, p.f_name)))
        return [schemas.Person.model_validate(p) for p in persons]
    
    @staticmethod
    @db_session
    def get_person(person_id: UUID) -> schemas.Person:
        """
        Liefert Details zu einer bestimmten Person.
        
        Args:
            person_id: Die UUID der Person.
            
        Returns:
            Details zur Person.
            
        Raises:
            PersonNotFoundException: Wenn die Person nicht gefunden wurde.
        """
        try:
            person = DBPerson.get(id=person_id)
            if not person:
                raise PersonNotFoundException(person_id=person_id)
            
            return schemas.Person.model_validate(person)
        except ObjectNotFound:
            raise PersonNotFoundException(person_id=person_id)
    
    @staticmethod
    @db_session
    def create_person(person_data: schemas.Person) -> schemas.Person:
        """
        Erstellt eine neue Person.
        
        Args:
            person_data: Die Daten für die neue Person.
            
        Returns:
            Die erstellte Person.
            
        Raises:
            DuplicatePersonException: Wenn bereits eine Person mit diesem Namen und dieser E-Mail existiert.
            PersonValidationException: Wenn die Validierung fehlschlägt.
        """
        # Validierung
        validation_errors = {}
        if not person_data.f_name or len(person_data.f_name.strip()) == 0:
            validation_errors["f_name"] = "Der Vorname darf nicht leer sein."
        if not person_data.l_name or len(person_data.l_name.strip()) == 0:
            validation_errors["l_name"] = "Der Nachname darf nicht leer sein."
            
        if validation_errors:
            raise PersonValidationException(errors=validation_errors)
        
        # Prüfen, ob bereits eine Person mit diesem Namen und dieser E-Mail existiert
        existing = DBPerson.select(
            lambda p: p.f_name == person_data.f_name and 
                     p.l_name == person_data.l_name and
                     p.email == person_data.email
        ).first()
        
        if existing:
            raise DuplicatePersonException(
                f_name=person_data.f_name,
                l_name=person_data.l_name,
                email=person_data.email,
                existing_id=existing.id
            )
        
        # Person erstellen
        person = DBPerson(
            f_name=person_data.f_name,
            l_name=person_data.l_name,
            email=person_data.email
        )
        
        return schemas.Person.model_validate(person)
    
    @staticmethod
    @db_session
    def update_person(person_id: UUID, person_data: schemas.Person) -> schemas.Person:
        """
        Aktualisiert eine bestehende Person.
        
        Args:
            person_id: Die UUID der zu aktualisierenden Person.
            person_data: Die neuen Daten für die Person.
            
        Returns:
            Die aktualisierte Person.
            
        Raises:
            PersonNotFoundException: Wenn die Person nicht gefunden wurde.
            DuplicatePersonException: Wenn bereits eine andere Person mit diesem Namen und dieser E-Mail existiert.
            PersonValidationException: Wenn die Validierung fehlschlägt.
        """
        # Validierung
        validation_errors = {}
        if not person_data.f_name or len(person_data.f_name.strip()) == 0:
            validation_errors["f_name"] = "Der Vorname darf nicht leer sein."
        if not person_data.l_name or len(person_data.l_name.strip()) == 0:
            validation_errors["l_name"] = "Der Nachname darf nicht leer sein."
            
        if validation_errors:
            raise PersonValidationException(errors=validation_errors)
            
        try:
            person = DBPerson.get(id=person_id)
            if not person:
                raise PersonNotFoundException(person_id=person_id)
                
            # Prüfen, ob bereits eine andere Person mit diesem Namen und dieser E-Mail existiert
            existing = DBPerson.select(
                lambda p: p.id != person_id and
                         p.f_name == person_data.f_name and 
                         p.l_name == person_data.l_name and
                         p.email == person_data.email
            ).first()
            
            if existing:
                raise DuplicatePersonException(
                    f_name=person_data.f_name,
                    l_name=person_data.l_name,
                    email=person_data.email,
                    existing_id=existing.id
                )
            
            # Person aktualisieren
            person.f_name = person_data.f_name
            person.l_name = person_data.l_name
            person.email = person_data.email
            
            return schemas.Person.model_validate(person)
        except ObjectNotFound:
            raise PersonNotFoundException(person_id=person_id)
    
    @staticmethod
    @db_session
    def delete_person(person_id: UUID) -> bool:
        """
        Löscht eine Person.
        
        Args:
            person_id: Die UUID der zu löschenden Person.
            
        Returns:
            True, wenn die Person erfolgreich gelöscht wurde.
            
        Raises:
            PersonNotFoundException: Wenn die Person nicht gefunden wurde.
            PersonInUseException: Wenn die Person noch in Terminen verwendet wird.
        """
        try:
            person = DBPerson.get(id=person_id)
            if not person:
                raise PersonNotFoundException(person_id=person_id)
                
            # Prüfen, ob die Person noch in Terminen verwendet wird
            appointment_count = count(a for a in person.appointments)
            if appointment_count > 0:
                raise PersonInUseException(
                    person_id=person_id,
                    appointment_count=appointment_count
                )
            
            # Person löschen
            person.delete()
            return True
        except ObjectNotFound:
            raise PersonNotFoundException(person_id=person_id)
    
    @staticmethod
    @db_session
    def search_persons(search_term: str, limit: int = 20) -> List[schemas.Person]:
        """
        Durchsucht Personen nach dem angegebenen Suchbegriff.
        
        Args:
            search_term: Der Suchbegriff.
            limit: Maximale Anzahl der Ergebnisse (Standard: 20).
            
        Returns:
            Eine Liste der passenden Personen.
        """
        if not search_term or len(search_term.strip()) < 2:
            return []
        
        search_term_lower = search_term.lower()
        
        persons = DBPerson.select(
            lambda p: search_term_lower in p.f_name.lower() or
                      search_term_lower in p.l_name.lower() or
                      (p.email and search_term_lower in p.email.lower())
        ).order_by(lambda p: (p.l_name, p.f_name))[:limit]
        
        return [schemas.Person.model_validate(p) for p in persons]
