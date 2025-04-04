from fastapi import APIRouter

from .appointments import router as appointments_router
from .plans import router as plans_router
from .locations import router as locations_router

api_router = APIRouter()
api_router.include_router(appointments_router, prefix="/appointments", tags=["appointments"])
api_router.include_router(plans_router, prefix="/plans", tags=["plans"])
api_router.include_router(locations_router, prefix="/locations", tags=["locations"])

__all__ = ['api_router']
