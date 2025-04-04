from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from .routes import api_router

# API-Objekt erstellen
app = FastAPI(
    title="Terminplanungs-API",
    description="API für die Terminplanungs-Webseite",
    version="0.1.0"
)

# API-Router einbinden
app.include_router(api_router, prefix="/api")

# Statische Dateien einbinden
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates konfigurieren
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)
