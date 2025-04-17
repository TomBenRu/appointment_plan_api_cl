from fastapi import APIRouter

from .calendar import router as calendar_main_router
from .locations import router as locations_router
from .persons import router as persons_router
from .plans import router as plans_router
from .search import router as search_router

# Kalender-Router erstellen
router = APIRouter()

# Kalender-Routen einbinden
router.include_router(calendar_main_router, tags=["web-calendar-main"])
router.include_router(locations_router, prefix="/locations", tags=["web-calendar-locations"])
router.include_router(persons_router, prefix="/persons", tags=["web-calendar-persons"])
router.include_router(plans_router, prefix="/plans", tags=["web-calendar-plans"])
router.include_router(search_router, prefix="/search", tags=["web-calendar-search"])

__all__ = ['router']
