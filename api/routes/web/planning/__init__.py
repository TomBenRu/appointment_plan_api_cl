from fastapi import APIRouter

from .planning import router as planning_main_router
from .availability import router as availability_router
from .periods import router as periods_router
from .teams import router as teams_router

# Planungs-Router erstellen
router = APIRouter()

# Planungs-Routen einbinden
router.include_router(planning_main_router, tags=["web-planning-main"])
router.include_router(availability_router, prefix="/availability", tags=["web-planning-availability"])
router.include_router(periods_router, prefix="/periods", tags=["web-planning-periods"])
router.include_router(teams_router, prefix="/teams", tags=["web-planning-teams"])

__all__ = ['router']
