from typing import List, Optional
from uuid import UUID

from pony.orm import db_session, select

from api.models import schemas
from database.models import LocationOfWork as DBLocationOfWork


class LocationService:
    @staticmethod
    @db_session
    def get_all_locations() -> List[schemas.LocationOfWorkDetail]:
        """
        Liefert eine Liste aller Arbeitsorte.
        """
        locations = list(DBLocationOfWork.select().order_by(lambda l: l.name))
        return [schemas.LocationOfWorkDetail.model_validate(l) for l in locations]
    
    @staticmethod
    @db_session
    def get_location(location_id: UUID) -> Optional[schemas.LocationOfWorkDetail]:
        """
        Liefert Details zu einem bestimmten Arbeitsort oder None, wenn nicht gefunden.
        """
        location = DBLocationOfWork.get(id=location_id)
        if not location:
            return None
        
        return schemas.LocationOfWorkDetail.model_validate(location)
    
    @staticmethod
    @db_session
    def search_locations(search_term: str, limit: int = 20) -> List[schemas.LocationOfWorkDetail]:
        """
        Durchsucht Arbeitsorte nach dem angegebenen Suchbegriff.
        """
        search_term_lower = search_term.lower()
        
        locations = DBLocationOfWork.select(
            lambda l: search_term_lower in l.name.lower() or
                      search_term_lower in l.address.street.lower() or
                      search_term_lower in l.address.city.lower() or
                      search_term_lower in l.address.postal_code.lower()
        ).order_by(lambda l: l.name)[:limit]
        
        return [schemas.LocationOfWorkDetail.model_validate(l) for l in locations]
