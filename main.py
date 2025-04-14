import contextlib
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from api import app
from api.routes import web_router
from database import setup_database
from api.middleware.error_handler import register_exception_handlers, exception_handler
from api.middleware.debug_route import DebugRoute

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug-Route aktivieren
app.router.route_class = DebugRoute

# CORS-Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception-Handler registrieren
register_exception_handlers(app)

# Auch HTTP-Statuscodes direkt behandeln
app.add_exception_handler(StarletteHTTPException, exception_handler)
app.add_exception_handler(404, exception_handler)  # Seite nicht gefunden
app.add_exception_handler(500, exception_handler)  # Serverfehler

# Debuggingmeldung
logger.info("Exception handlers registered")

@contextlib.asynccontextmanager
async def lifespan(app):
    # Startup
    setup_database()
    logger.info("Database setup complete")
    yield
    # Shutdown
    pass

# Lifespan-Event-Handler zuweisen
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    # Server starten mit Hot-Reload
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
