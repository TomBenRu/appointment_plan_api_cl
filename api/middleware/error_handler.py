"""
Middleware zur Behandlung von Exceptions.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from pony.orm.core import ObjectNotFound

from api.exceptions import (
    # Base exceptions
    AppBaseException, ResourceNotFoundException, ValidationException,
    ConflictException, PermissionDeniedException,
    
    # Appointment exceptions
    AppointmentNotFoundException, AppointmentOverlapException,
    InvalidAppointmentDateException, AppointmentUpdateConflictException,
    
    # Location exceptions
    LocationNotFoundException, LocationInUseException,
    DuplicateLocationException, LocationValidationException,
    
    # Person exceptions
    PersonNotFoundException, PersonInUseException,
    DuplicatePersonException, PersonValidationException,
    
    # Plan exceptions
    PlanNotFoundException, PlanPeriodNotFoundException, PlanInUseException,
    DuplicatePlanException, PlanValidationException, PlanPeriodOverlapException
)
from api.templates import templates  # Importiere die Jinja2-Templates


def _is_htmx_request(request: Request) -> bool:
    """
    Prüft, ob es sich um eine HTMX-Anfrage handelt.
    
    Args:
        request: Die aktuelle Request.
        
    Returns:
        True, wenn es sich um eine HTMX-Anfrage handelt, sonst False.
    """
    # HTMX-Anfragen beginnen mit /hx/
    path = request.url.path
    return path.startswith("/hx/")


async def exception_handler(request: Request, exc: Exception):
    """
    Zentraler Exception-Handler für alle anwendungsspezifischen Exceptions.
    
    Args:
        request: Die aktuelle Request.
        exc: Die aufgetretene Exception.
        
    Returns:
        JSONResponse mit entsprechendem Statuscode und Fehlermeldung oder
        HTMLResponse für Web-Anfragen.
    """
    # Logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Exception: {exc}")
    
    # Prüfen, welche Art von Anfrage vorliegt
    is_web_request = _is_web_request(request)
    is_htmx_request = _is_htmx_request(request)
    
    # Bei benutzerdefinierten Exceptions
    if isinstance(exc, AppBaseException):
        if is_htmx_request:
            return await _render_htmx_error(
                request=request,
                status_code=exc.status_code,
                title=_get_error_title(exc.status_code),
                message=exc.message,
                details=exc.details
            )
        elif is_web_request:
            return await _render_html_error(
                request=request,
                status_code=exc.status_code,
                title=_get_error_title(exc.status_code),
                message=exc.message,
                details=exc.details
            )
        else:
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict()
            )
    
    # Bei Validierungsfehlern (Pydantic)
    if isinstance(exc, RequestValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = "Validierungsfehler bei der Anfrage"
        details = {"validation_errors": exc.errors()}
        
        if is_htmx_request:
            return await _render_htmx_error(
                request=request,
                status_code=status_code,
                title="Validierungsfehler",
                message=message,
                details=details
            )
        elif is_web_request:
            return await _render_html_error(
                request=request,
                status_code=status_code,
                title="Validierungsfehler",
                message=message,
                details=details
            )
        else:
            return JSONResponse(
                status_code=status_code,
                content={
                    "message": message,
                    "status_code": status_code,
                    "details": details
                }
            )
    
    # Bei PonyORM ObjectNotFound
    if isinstance(exc, ObjectNotFound):
        status_code = status.HTTP_404_NOT_FOUND
        message = "Die angeforderte Ressource wurde nicht gefunden"
        details = {"error": str(exc)}
        
        if is_htmx_request:
            return await _render_htmx_error(
                request=request,
                status_code=status_code,
                title="Nicht gefunden",
                message=message,
                details=details
            )
        elif is_web_request:
            return await _render_html_error(
                request=request,
                status_code=status_code,
                title="Nicht gefunden",
                message=message,
                details=details
            )
        else:
            return JSONResponse(
                status_code=status_code,
                content={
                    "message": message,
                    "status_code": status_code,
                    "details": details
                }
            )
    
    # Bei sonstigen Exceptions
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Ein interner Serverfehler ist aufgetreten"
    details = {"error": str(exc)}
    
    if is_htmx_request:
        return await _render_htmx_error(
            request=request,
            status_code=status_code,
            title="Serverfehler",
            message=message,
            details=details
        )
    elif is_web_request:
        return await _render_html_error(
            request=request,
            status_code=status_code,
            title="Serverfehler",
            message=message,
            details=details
        )
    else:
        return JSONResponse(
            status_code=status_code,
            content={
                "message": message,
                "status_code": status_code,
                "details": details
            }
        )


def _is_web_request(request: Request) -> bool:
    """
    Prüft, ob es sich um eine Web-Anfrage (HTML) oder API-Anfrage (JSON) handelt.
    
    Args:
        request: Die aktuelle Request.
        
    Returns:
        True, wenn es sich um eine Web-Anfrage handelt, sonst False.
    """
    # Browser-Anfrage erkennen: Pfade ohne /api/ und ohne /hx/ sind Web-Anfragen
    path = request.url.path
    return not (path.startswith("/api/") or path.startswith("/hx/"))


async def _render_html_error(
    request: Request,
    status_code: int,
    title: str,
    message: str,
    details: dict = None
) -> HTMLResponse:
    """
    Rendert eine HTML-Fehlerseite.
    
    Args:
        request: Die aktuelle Request.
        status_code: Der HTTP-Statuscode.
        title: Der Titel der Fehlerseite.
        message: Die Fehlermeldung.
        details: Optionale Details zum Fehler.
        
    Returns:
        Eine HTML-Response mit der gerenderten Fehlerseite.
    """
    content = templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": status_code,
            "title": title,
            "message": message,
            "details": details
        }
    )
    content.status_code = status_code
    
    # Cache-Header setzen, um Browser-Caching zu deaktivieren
    content.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    return content


async def _render_htmx_error(
    request: Request,
    status_code: int,
    title: str,
    message: str,
    details: dict = None
) -> HTMLResponse:
    """
    Rendert ein HTML-Fragment für HTMX-Fehlerantworten.
    
    Args:
        request: Die aktuelle Request.
        status_code: Der HTTP-Statuscode.
        title: Der Titel der Fehlerseite.
        message: Die Fehlermeldung.
        details: Optionale Details zum Fehler.
        
    Returns:
        Eine HTML-Response mit einem einfachen Fehlerfragment und Status 200.
    """
    content = templates.TemplateResponse(
        "htmx_error.html",
        {
            "request": request,
            "status_code": status_code,
            "title": title,
            "message": message,
            "details": details
        }
    )
    
    # Wichtig: Status 200 zurückgeben, damit HTMX die Antwort verarbeitet
    content.status_code = 200
    
    # HTMX-Header hinzufügen
    content.headers["HX-Trigger"] = '{"showMessage": {"level": "error", "message": "' + message + '"}}'  
    
    # Cache-Header setzen, um Browser-Caching zu deaktivieren
    content.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    return content


def _get_error_title(status_code: int) -> str:
    """
    Gibt einen benutzerfreundlichen Titel für einen HTTP-Statuscode zurück.
    
    Args:
        status_code: Der HTTP-Statuscode.
        
    Returns:
        Ein benutzerfreundlicher Titel.
    """
    titles = {
        400: "Ungültige Anfrage",
        401: "Nicht autorisiert",
        403: "Zugriff verweigert",
        404: "Nicht gefunden",
        409: "Konflikt",
        422: "Validierungsfehler",
        500: "Serverfehler"
    }
    return titles.get(status_code, "Fehler")


def register_exception_handlers(app):
    """
    Registriert alle Exception-Handler bei der FastAPI-Anwendung.
    
    Args:
        app: Die FastAPI-Anwendung.
    """
    # Eigene Exception-Klassen (Basisklassen reichen, da Vererbung)
    app.add_exception_handler(AppBaseException, exception_handler)
    app.add_exception_handler(RequestValidationError, exception_handler)
    app.add_exception_handler(ObjectNotFound, exception_handler)
    
    # Allgemeiner Fallback für alle anderen Exceptions
    app.add_exception_handler(Exception, exception_handler)
