from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from .routes import api_router, web_router

# API-Objekt erstellen
app = FastAPI(
    title="Terminplanungs-API",
    description="API für die Terminplanungs-Webseite",
    version="0.1.0"
)

# API-Router einbinden
app.include_router(api_router, prefix="/api")

# Web-Routen einbinden
app.include_router(web_router, tags=["web"])

# Statische Dateien einbinden
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
