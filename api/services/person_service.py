from typing import List, Optional
from uuid import UUID

from pony.orm import db_session, select

from api.models import schemas
from database.models import Person as DBPerson


class PersonService:
    @staticmethod
    @db_session
    def get_all_persons() -> List[schemas.Person]:
        """
        Liefert eine Liste aller Personen.
        """
        persons = list(DBPerson.select().order_by(lambda p: (p.l_name, p.f_name)))
        return [schemas.Person.model_validate(p) for p in persons]
    
    @staticmethod
    @db_session
    def get_person(person_id: UUID) -> Optional[schemas.Person]:
        """
        Liefert Details zu einer bestimmten Person oder None, wenn nicht gefunden.
        """
        person = DBPerson.get(id=person_id)
        if not person:
            return None
        
        return schemas.Person.model_validate(person)
    
    @staticmethod
    @db_session
    def search_persons(search_term: str, limit: int = 20) -> List[schemas.Person]:
        """
        Durchsucht Personen nach dem angegebenen Suchbegriff.
        """
        search_term_lower = search_term.lower()
        
        persons = DBPerson.select(
            lambda p: search_term_lower in p.f_name.lower() or
                      search_term_lower in p.l_name.lower() or
                      (p.email and search_term_lower in p.email.lower())
        ).order_by(lambda p: (p.l_name, p.f_name))[:limit]
        
        return [schemas.Person.model_validate(p) for p in persons]
