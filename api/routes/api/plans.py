from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException

from api.models import schemas
from api.services import PlanService

router = APIRouter()

@router.get("/", response_model=List[schemas.Plan])
def get_plans(plan_period_id: Optional[UUID] = None):
    """
    Liefert eine Liste aller Pläne, optional gefiltert nach Planungsperiode.
    """
    # PlanService nutzen
    plan_service = PlanService()
    
    if plan_period_id:
        return plan_service.get_plans_by_period(plan_period_id)
    else:
        return plan_service.get_all_plans()


@router.get("/{plan_id}", response_model=schemas.PlanDetail)
def get_plan(plan_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Plan.
    """
    # PlanService nutzen
    plan_service = PlanService()
    plan_detail = plan_service.get_plan_detail(plan_id)
    
    if not plan_detail:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")
    
    return plan_detail
