"""
Middleware zur Behandlung von Exceptions.
"""
from fastapi import Request, status, HTTPException, FastAPI
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
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
from api.utils import MenuDisplaySection


def _is_htmx_request(request: Request) -> bool:
    """
    Prüft, ob es sich um eine HTMX-Anfrage handelt.
    
    Args:
        request: Die aktuelle Request.
        
    Returns:
        True, wenn es sich um eine HTMX-Anfrage handelt, sonst False.
    """
    # HTMX setzt den HX-Request Header
    return "HX-Request" in request.headers


def _is_web_request(request: Request) -> bool:
    """
    Prüft, ob es sich um eine Web-Anfrage (HTML) oder API-Anfrage (JSON) handelt.

    Args:
        request: Die aktuelle Request.

    Returns:
        True, wenn es sich um eine Web-Anfrage handelt, sonst False.
    """
    # Browser-Anfrage erkennen: Pfade ohne /api/ sind Web-Anfragen
    path = request.url.path
    return not path.startswith("/api/")


async def exception_handler(request: Request, exc: Exception):
    """
    Zentraler Exception-Handler für alle anwendungsspezifischen Exceptions.
    """
    # Logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Debug exception_handler: path={request.url.path}, exception={exc}")
    
    # Prüfen, welche Art von Anfrage vorliegt
    is_web_request = _is_web_request(request)
    is_htmx_request = _is_htmx_request(request)
    
    # Bei HTTPException (inkl. 401/403 für Auth)
    if isinstance(exc, HTTPException):
        # Authorization-Fehler speziell behandeln
        if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            # Für normale Web-Anfragen
            if is_web_request and not is_htmx_request:
                # Login-Modal anzeigen (der Status ist bereits in der Request gespeichert)
                # Für reguläre Anfragen zur Startseite weiterleiten
                if exc.status_code == status.HTTP_401_UNAUTHORIZED:
                    # Wenn der Pfad nicht die Startseite ist, dorthin umleiten
                    if request.url.path != "/":
                        return RedirectResponse(
                            url="/",
                            status_code=status.HTTP_303_SEE_OTHER
                        )
                    
                    # Bei 401 auf der Startseite nur 200 zurückgeben und Template rendern
                    # (das Login-Modal wird vom Template angezeigt)
                    from api.services import CalendarService
                    calendar_service = CalendarService()
                    
                    # Aktuelles Datum
                    from datetime import date
                    today = date.today()
                    
                    # Kalenderdaten für den aktuellen Monat erstellen
                    calendar_weeks = calendar_service.get_calendar_data(today.year, today.month)
                    
                    # Termine in den Kalender einfügen ohne Filter
                    calendar_weeks = calendar_service.fill_calendar_with_appointments(calendar_weeks)
                    
                    # Filter-Optionen laden
                    filter_options = calendar_service.get_filter_options()
                    
                    response = templates.TemplateResponse(
                        "index.html",
                        {
                            "request": request,
                            "show_login_modal": True,
                            "required_role": getattr(request.state, "required_role", None),
                            "calendar_weeks": calendar_weeks,
                            "year": today.year,
                            "month": today.month,
                            "month_name": calendar_service.get_month_name(today.month),
                            "today": today,
                            "active_filters": {},
                            "filter_person_id": None,
                            "filter_location_id": None,
                            "all_persons": filter_options["all_persons"],
                            "all_locations": filter_options["all_locations"],
                            "menu_section": MenuDisplaySection.NONE
                        }
                    )
                    return response
                
                # Bei 403 eine normale Fehlerseite anzeigen
                return await _render_html_error(
                    request=request,
                    status_code=exc.status_code,
                    title=_get_error_title(exc.status_code),
                    message=exc.detail,
                    details={}
                )
        # Alle anderen HTTPExceptions normal behandeln
        if is_htmx_request:
            return await _render_htmx_error(
                request=request,
                status_code=exc.status_code,
                title=_get_error_title(exc.status_code),
                message=exc.detail,
                details={}
            )
        elif is_web_request:
            return await _render_html_error(
                request=request,
                status_code=exc.status_code,
                title=_get_error_title(exc.status_code),
                message=exc.detail,
                details={}
            )
        else:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "message": exc.detail,
                    "status_code": exc.status_code
                }
            )
    
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
            "details": details,
            "menu_section": MenuDisplaySection.NONE
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
    Rendert ein HTML-Fragment für HTMX-Fehlerantworten mit OOB-Swap.
    
    Args:
        request: Die aktuelle Request.
        status_code: Der HTTP-Statuscode.
        title: Der Titel der Fehlerseite.
        message: Die Fehlermeldung.
        details: Optionale Details zum Fehler.
        
    Returns:
        Eine HTML-Response mit einem OOB-Swap für die Fehlermeldung.
    """
    # Fehlermeldung als OOB-Swap
    error_response = templates.TemplateResponse(
        "error_message.html",
        {
            "request": request,
            "title": title,
            "message": message,
            "details": details
        }
    )
    
    # Status 200 zurückgeben, damit HTMX die Antwort verarbeitet
    error_response.status_code = 200
    
    # Cache-Header setzen, um Browser-Caching zu deaktivieren
    error_response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    
    return error_response


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


def register_exception_handlers(app: FastAPI):
    """
    Registriert alle Exception-Handler bei der FastAPI-Anwendung.
    
    Args:
        app: Die FastAPI-Anwendung.
    """
    # Eigene Exception-Klassen (Basisklassen reichen, da Vererbung)
    app.add_exception_handler(AppBaseException, exception_handler)
    app.add_exception_handler(RequestValidationError, exception_handler)
    app.add_exception_handler(ObjectNotFound, exception_handler)
    app.add_exception_handler(HTTPException, exception_handler)  # HTTPException explizit hinzufügen
    
    # Allgemeiner Fallback für alle anderen Exceptions
    app.add_exception_handler(Exception, exception_handler)
