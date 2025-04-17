from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from api.auth.cookie_auth import require_web_employee
from api.auth.models import User
from api.templates import templates
from api.utils import MenuDisplaySection

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def planning_index(
    request: Request,
    user: Optional[User] = Depends(require_web_employee)
):
    """Startseite für die Einsatzplanung."""
    return templates.TemplateResponse(
        "planning_placeholder.html",
        {
            "request": request,
            "user": user,
            "menu_section": MenuDisplaySection.PLANNING
        }
    )
