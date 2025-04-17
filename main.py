from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import api_router, web_router
from database import setup_database
from api.middleware.error_handler import register_exception_handlers

# Lifespan-Kontext-Manager für Anwendungsstart und -ende
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_database()
    print("Datenbank initialisiert")
    yield
    # Shutdown
    pass

# FastAPI-App erstellen
app = FastAPI(lifespan=lifespan)

# API-Routen einbinden
app.include_router(api_router, prefix="/api")

# Web-Routen einbinden (beinhaltet jetzt auch die Planning-Routen)
app.include_router(web_router, tags=["web"])

# Statische Dateien
app.mount("/static", StaticFiles(directory="static"), name="static")

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

if __name__ == "__main__":
    # Server starten
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
