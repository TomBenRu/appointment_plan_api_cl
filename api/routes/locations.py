from typing import List
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException
from pony.orm import db_session, select

from api.models import schemas
from database.models import LocationOfWork as DBLocationOfWork

router = APIRouter()

@router.get("/", response_model=List[schemas.LocationOfWork])
@db_session
def get_locations():
    """
    Liefert eine Liste aller Arbeitsorte.
    """
    locations = list(select(l for l in DBLocationOfWork))
    return [schemas.LocationOfWork.model_validate(l) for l in locations]


@router.get("/{location_id}", response_model=schemas.LocationOfWorkDetail)
@db_session
def get_location(location_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Arbeitsort.
    """
    location = DBLocationOfWork.get(id=location_id)
    if not location:
        raise HTTPException(status_code=404, detail="Arbeitsort nicht gefunden")
    
    return schemas.LocationOfWorkDetail.model_validate(location)
