"""
Middleware zur Behandlung von Exceptions.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from pony.orm.core import ObjectNotFound

from api.exceptions import (
    AppBaseException, ResourceNotFoundException, ValidationException,
    ConflictException, PermissionDeniedException
)
from api.templates import templates  # Importiere die Jinja2-Templates


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
    # Prüfen, ob es sich um eine Web-Anfrage handelt (basierend auf dem Accept-Header oder URL-Pfad)
    is_web_request = _is_web_request(request)
    print(f'Debug: {is_web_request=}, {exc=}')
    
    # Wenn es sich um eine unserer benutzerdefinierten Exceptions handelt
    if isinstance(exc, AppBaseException):
        print(f"Benutzerdefinierte Exception: {exc}")
        if is_web_request:
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
    
    # FastAPI Validierungsfehler (z.B. bei Pydantic-Modellen)
    if isinstance(exc, RequestValidationError):
        print(f"Validierungsfehler: {exc}")
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        message = "Validierungsfehler bei der Anfrage"
        details = {"validation_errors": exc.errors()}
        
        if is_web_request:
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
    
    # PonyORM ObjectNotFound-Exception
    if isinstance(exc, ObjectNotFound):
        print(f"ObjectNotFound: {exc}")
        status_code = status.HTTP_404_NOT_FOUND
        message = "Die angeforderte Ressource wurde nicht gefunden"
        details = {"error": str(exc)}
        
        if is_web_request:
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
    
    # Allgemeiner Serverfehler für unbehandelte Exceptions
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Ein interner Serverfehler ist aufgetreten"
    details = {"error": str(exc)}

    print(f"Unbehandelte Exception: {exc}")
    
    if is_web_request:
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
    # Pfadbasierte Erkennung (alle Pfade außer denen, die mit /api beginnen, gelten als Web-Anfragen)
    path = request.url.path
    if not path.startswith("/api/"):
        return True
    
    # Accept-Header basierte Erkennung als Fallback
    accept_header = request.headers.get("accept", "")
    return "text/html" in accept_header and "application/json" not in accept_header


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
