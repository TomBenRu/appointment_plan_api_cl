import contextlib
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from api import app
from api.web_routes import router as web_router
from database import setup_database

# Web-Routen einbinden
app.include_router(web_router)

# CORS-Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@contextlib.asynccontextmanager
async def lifespan(app):
    # Startup
    setup_database()
    yield
    # Shutdown
    pass

# Lifespan-Event-Handler zuweisen
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    # Server starten mit Hot-Reload
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)