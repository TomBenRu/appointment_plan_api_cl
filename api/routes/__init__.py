from fastapi import APIRouter, Depends

from api.auth import require_employee
from .appointments import router as appointments_router
from .plans import router as plans_router
from .locations import router as locations_router
from .auth import router as auth_router
from .web_auth import router as web_auth_router
from .web import router as web_router
from .planning import router as planning_router

api_router = APIRouter()

# Auth-Router ohne Abhängigkeiten
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Web-Auth-Router ohne Abhängigkeiten
web_router.include_router(web_auth_router, prefix="/auth", tags=["web-auth"])

# API-Routen mit Rollenabhängigkeit (employee)
api_router.include_router(
    appointments_router, 
    prefix="/appointments", 
    tags=["appointments"],
    dependencies=[Depends(require_employee)]
)
api_router.include_router(
    plans_router, 
    prefix="/plans", 
    tags=["plans"],
    dependencies=[Depends(require_employee)]
)
api_router.include_router(
    locations_router, 
    prefix="/locations", 
    tags=["locations"],
    dependencies=[Depends(require_employee)]
)

__all__ = ['api_router', 'web_router', 'planning_router']
