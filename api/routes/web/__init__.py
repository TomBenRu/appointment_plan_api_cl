from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from api.auth.models import User
from api.templates import templates
from api.utils import MenuDisplaySection

from typing import Optional

from .auth import router as auth_router
from .calendar import router as calendar_router
from .planning import router as planning_router
from ...auth import require_web_guest

# Web-Router erstellen
router = APIRouter()

# Auth-Router einbinden
router.include_router(auth_router, prefix="/auth", tags=["web-auth"])

# Kalender-Router einbinden
router.include_router(calendar_router, prefix="/calendar", tags=["web-calendar"])

# Planungs-Router einbinden
router.include_router(planning_router, prefix="/planning", tags=["web-planning"])

@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    user: Optional[User] = Depends(require_web_guest)
):
    """Homepage mit Landing-Page."""
    # Prüfen, ob login_modal angezeigt werden soll
    show_login_modal = getattr(request.state, "show_login_modal", False)
    required_role = getattr(request.state, "required_role", None)
    # Template rendern
    return templates.TemplateResponse(
        "landing_page.html",
        {
            "request": request,
            "show_login_modal": show_login_modal,
            "required_role": required_role,
            "user": user,
            "menu_section": MenuDisplaySection.NONE
        }
    )

__all__ = ['router']
