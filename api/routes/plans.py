from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Path, HTTPException
from pony.orm import db_session, select

from api.models import schemas
from database.models import Plan as DBPlan
from api.routes.appointments import add_end_time_str  # Wir importieren die Funktion für AppointmentLinks

router = APIRouter()

@router.get("/", response_model=List[schemas.Plan])
@db_session
def get_plans(plan_period_id: Optional[UUID] = None):
    """
    Liefert eine Liste aller Pläne, optional gefiltert nach Planungsperiode.
    """
    query = select(p for p in DBPlan)
    
    if plan_period_id:
        query = query.filter(lambda p: p.plan_period.id == plan_period_id)
    
    plans = list(query)
    return [schemas.Plan.model_validate(p) for p in plans]


@router.get("/{plan_id}", response_model=schemas.PlanDetail)
@db_session
def get_plan(plan_id: UUID = Path(...)):
    """
    Liefert Details zu einem bestimmten Plan.
    """
    plan = DBPlan.get(id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")
    
    # Beim PlanDetail müssen wir die Appointments mit end_time_str anreichern
    plan_detail = schemas.PlanDetail.model_validate(plan)
    
    # Füge end_time_str zu jedem Appointment hinzu
    for i, appointment in enumerate(plan_detail.appointments):
        # Der Einfachheit halber nehmen wir direkt die Originaldaten
        db_appointment = plan.appointments[i]
        appointment_with_end_time = add_end_time_str(db_appointment)
        plan_detail.appointments[i] = appointment_with_end_time
    
    return plan_detail
