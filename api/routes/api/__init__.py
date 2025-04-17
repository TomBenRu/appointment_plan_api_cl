from fastapi import APIRouter, Depends

from api.auth import require_employee
from .appointments import router as appointments_router
from .plans import router as plans_router
from .locations import router as locations_router
from .auth import router as auth_router

# API-Router erstellen
router = APIRouter()

# Auth-Router ohne Abhängigkeiten
router.include_router(auth_router, prefix="/auth", tags=["auth"])

# API-Routen mit Rollenabhängigkeit (employee)
router.include_router(
    appointments_router, 
    prefix="/appointments", 
    tags=["appointments"],
    dependencies=[Depends(require_employee)]
)
router.include_router(
    plans_router, 
    prefix="/plans", 
    tags=["plans"],
    dependencies=[Depends(require_employee)]
)
router.include_router(
    locations_router, 
    prefix="/locations", 
    tags=["locations"],
    dependencies=[Depends(require_employee)]
)

__all__ = ['router']
