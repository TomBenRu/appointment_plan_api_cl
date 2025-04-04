from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException
from pony.orm import db_session, select

from api.models import Plan, PlanDetail
from database.models import Plan as DBPlan
from api.utils.converters import plan_to_schema, plan_to_detail_schema

router = APIRouter()

@router.get("/", response_model=List[Plan])
@db_session
def get_plans(plan_period_id: Optional[UUID] = None):
    """
    Liefert eine Liste aller Pläne, optional gefiltert nach Planungsperiode.
    """
    query = select(p for p in DBPlan)
    
    if plan_period_id:
        query = query.filter(lambda p: p.plan_period.id == plan_period_id)
    
    plans = list(query)
    return [plan_to_schema(p) for p in plans]


@router.get("/{plan_id}", response_model=PlanDetail)
@db_session
def get_plan(plan_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Plan.
    """
    plan = DBPlan.get(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")
    
    return plan_to_detail_schema(plan)
