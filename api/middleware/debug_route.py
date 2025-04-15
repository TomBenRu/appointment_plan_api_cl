from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
import traceback
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebugRoute(APIRoute):
    """
    Benutzerdefinierte Route, die Exceptions protokolliert und dann weiterleitet.
    """
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                logger.error(f"Exception in route {request.url.path}:\n{traceback_str}")
                raise
                
        return custom_route_handler
