# Wichtige Commands - appointment_plan_api_cl

## Entwicklungsserver starten
```bash
python main.py
```
- Startet FastAPI mit Uvicorn
- Server läuft auf: http://127.0.0.1:8000
- API-Dokumentation: http://127.0.0.1:8000/docs

## Package Management (uv)
```bash
# Abhängigkeiten installieren
uv sync

# Projekt im Development-Modus installieren
uv pip install -e .

# Neue Abhängigkeit hinzufügen
uv add <package-name>

# Development-Abhängigkeit hinzufügen
uv add --dev <package-name>
```

## Code-Qualität & Formatierung
```bash
# Code formatieren (Black)
uv run black .

# Imports sortieren (isort)
uv run isort .

# Type-Checking (mypy)
uv run mypy .

# Alles zusammen (Empfohlen vor Commit)
uv run black . && uv run isort . && uv run mypy .
```

## Testing
```bash
# Tests ausführen
uv run pytest

# Tests mit Coverage
uv run pytest --cov=api --cov=database

# Spezifische Test-Datei
uv run pytest tests/test_appointments.py

# Tests mit Verbose Output
uv run pytest -v
```

## Datenbank-Operationen
```bash
# Admin-Benutzer erstellen
python create_admin.py

# Datenbank-Setup (automatisch beim App-Start)
# Wird in main.py -> lifespan -> setup_database() ausgeführt
```

## Entwicklungs-Workflow
```bash
# 1. Änderungen machen
# 2. Code formatieren
uv run black . && uv run isort .

# 3. Type-Checking
uv run mypy .

# 4. Tests ausführen
uv run pytest

# 5. Server für manuellen Test starten
python main.py
```

## Git-Workflow (Windows)
```bash
# Status prüfen
git status

# Änderungen hinzufügen
git add .

# Commit mit Nachricht
git commit -m "feat: neue Funktion hinzugefügt"

# Push
git push origin main
```

## Produktions-Deployment
```bash
# Mit Umgebungsvariable für PostgreSQL
set DATABASE_URL=postgresql://user:password@localhost/dbname
python main.py

# Oder in production:
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Debugging & Logs
```bash
# App im Debug-Modus starten (mit reload)
uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# SQLite-Datenbank direkt anzeigen
# Datei: data/appointments.sqlite
# Mit DBeaver oder ähnlichem Tool öffnen
```

## System-spezifische Commands (Windows)
```bash
# Projektverzeichnis navigieren
cd C:\Users\tombe\PycharmProjects\appointment_plan_api_cl

# Python-Version prüfen
python --version

# Virtuelle Umgebung aktivieren (falls uv nicht verwendet)
.venv\Scripts\activate

# Port prüfen (ob 8000 belegt)
netstat -an | findstr 8000
```
