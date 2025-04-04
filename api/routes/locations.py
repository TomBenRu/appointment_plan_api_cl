from typing import List
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException
from pony.orm import db_session, select

from api.models import LocationOfWork, LocationOfWorkDetail
from database.models import LocationOfWork as DBLocationOfWork
from api.utils.converters import location_to_schema, location_to_detail_schema

router = APIRouter()

@router.get("/", response_model=List[LocationOfWork])
@db_session
def get_locations():
    """
    Liefert eine Liste aller Arbeitsorte.
    """
    locations = list(select(l for l in DBLocationOfWork))
    return [location_to_schema(l) for l in locations]


@router.get("/{location_id}", response_model=LocationOfWorkDetail)
@db_session
def get_location(location_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Arbeitsort.
    """
    location = DBLocationOfWork.get(uuid=str(location_id))
    if not location:
        raise HTTPException(status_code=404, detail="Arbeitsort nicht gefunden")
    
    return location_to_detail_schema(location)
