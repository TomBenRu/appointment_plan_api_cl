from typing import List
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException

from api.models import schemas
from api.services import LocationService

router = APIRouter()

@router.get("/", response_model=List[schemas.LocationOfWorkDetail])
def get_locations():
    """
    Liefert eine Liste aller Arbeitsorte.
    """
    # LocationService nutzen, um alle Arbeitsorte zu laden
    location_service = LocationService()
    return location_service.get_all_locations()


@router.get("/{location_id}", response_model=schemas.LocationOfWorkDetail)
def get_location(location_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Arbeitsort.
    """
    # LocationService nutzen, um Arbeitsortdetails zu laden
    location_service = LocationService()
    location = location_service.get_location(location_id)
    
    if not location:
        raise HTTPException(status_code=404, detail="Arbeitsort nicht gefunden")
    
    return location
