"""
Middleware zur Behandlung von Exceptions.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pony.orm.core import ObjectNotFound

from api.exceptions import (
    AppBaseException, ResourceNotFoundException, ValidationException,
    ConflictException, PermissionDeniedException
)


async def exception_handler(request: Request, exc: Exception):
    """
    Zentraler Exception-Handler für alle anwendungsspezifischen Exceptions.
    
    Args:
        request: Die aktuelle Request.
        exc: Die aufgetretene Exception.
        
    Returns:
        JSONResponse mit entsprechendem Statuscode und Fehlermeldung.
    """
    # Wenn es sich um eine unserer benutzerdefinierten Exceptions handelt
    if isinstance(exc, AppBaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )
    
    # FastAPI Validierungsfehler (z.B. bei Pydantic-Modellen)
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validierungsfehler bei der Anfrage",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "details": {
                    "validation_errors": exc.errors()
                }
            }
        )
    
    # PonyORM ObjectNotFound-Exception
    if isinstance(exc, ObjectNotFound):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Die angeforderte Ressource wurde nicht gefunden",
                "status_code": status.HTTP_404_NOT_FOUND,
                "details": {
                    "error": str(exc)
                }
            }
        )
    
    # Allgemeiner Serverfehler für unbehandelte Exceptions
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Ein interner Serverfehler ist aufgetreten",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "details": {
                "error": str(exc)
            }
        }
    )


def register_exception_handlers(app):
    """
    Registriert alle Exception-Handler bei der FastAPI-Anwendung.
    
    Args:
        app: Die FastAPI-Anwendung.
    """
    # Eigene Exception-Klassen
    app.add_exception_handler(AppBaseException, exception_handler)
    app.add_exception_handler(ResourceNotFoundException, exception_handler)
    app.add_exception_handler(ValidationException, exception_handler)
    app.add_exception_handler(ConflictException, exception_handler)
    app.add_exception_handler(PermissionDeniedException, exception_handler)
    
    # FastAPI und PonyORM spezifische Exceptions
    app.add_exception_handler(RequestValidationError, exception_handler)
    app.add_exception_handler(ObjectNotFound, exception_handler)
    
    # Allgemeiner Fallback für alle anderen Exceptions
    app.add_exception_handler(Exception, exception_handler)
