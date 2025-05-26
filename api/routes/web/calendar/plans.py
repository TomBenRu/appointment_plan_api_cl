from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from api.services import PlanService
from api.templates import templates
from api.auth.cookie_auth import require_web_employee
from api.auth.models import User
from api.utils import MenuDisplaySection

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def plans(
    request: Request,
    user: Optional[User] = Depends(require_web_employee)
):
    """Seite mit Plänen."""
    # PlanService nutzen, um alle Pläne zu laden
    plan_service = PlanService()
    plans_data = plan_service.get_all_plans()
    
    # Template rendern
    return templates.TemplateResponse(
        "plans.html",
        {
            "request": request,
            "plans": plans_data,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )

@router.get("/{plan_id}", response_class=HTMLResponse)
def plan_detail(
    request: Request, 
    plan_id: UUID,
    user: Optional[User] = Depends(require_web_employee)
):
    """Detailseite für einen Plan."""
    # PlanService nutzen, um Plandetails zu laden
    plan_service = PlanService()
    plan_detail = plan_service.get_plan_detail(plan_id)

    if not plan_detail:
        raise HTTPException(status_code=404, detail="Plan nicht gefunden")

    # Template rendern
    return templates.TemplateResponse(
        "plan_detail.html",
        {
            "request": request,
            "plan": plan_detail,
            "user": user,
            "menu_section": MenuDisplaySection.CALENDAR
        }
    )
