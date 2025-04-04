# Terminplanungs-Webseite

Eine Webseite zur Anzeige von geplanten Terminen mit einer Kalenderansicht.

## Technologien

- **Backend**: FastAPI mit Pydantic und PonyORM
- **Frontend**: Jinja2 Templates, Tailwind CSS, Alpine.js und HTMX, wenn möglich Verzicht auf JavaScript
- **Datenbank**: SQLite (Entwicklung) / PostgreSQL (Produktion)

## Projektstruktur

```
appointment_plan_api_cl/
├── api/                # API-Implementierung
│   ├── models/         # Pydantic-Schemas
│   ├── routes/         # API-Endpunkte
│   ├── utils/          # Hilfsfunktionen
│   └── web_routes.py   # Web-Routen für HTML-Seiten
├── database/           # Datenbankzugriff
│   └── models/         # PonyORM-Entitäten
├── static/             # Statische Dateien (CSS, JS, etc.)
│   └── css/            # CSS-Dateien
├── templates/          # Jinja2-Templates
├── main.py             # Hauptanwendungsdatei
└── pyproject.toml      # Projekteinstellungen
```

## Installation

1. Python 3.12 oder höher installieren
2. Repository klonen
3. Abhängigkeiten installieren:
   ```bash
   pip install -e .
   ```

## Entwicklung

Zum Starten des Entwicklungsservers:

```bash
python main.py
```

Der Server ist dann unter [http://127.0.0.1:8000](http://127.0.0.1:8000) erreichbar.

## API-Dokumentation

Die API-Dokumentation ist unter [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) verfügbar.

## Funktionen

- Kalenderansicht der geplanten Termine
- Navigation zwischen Monaten
- Detailansicht von Terminen
- Responsive Design für verschiedene Geräte

## Datenmodell

### Address
```python
class Address(pydantic.BaseModel):
    id: UUID          # Eindeutige ID der Adresse
    street: str       # Straße und Hausnummer
    postal_code: str  # Postleitzahl
    city: str         # Stadt
```

### LocationOfWork
```python
class LocationOfWork(pydantic.BaseModel):
    id: UUID      # Eindeutige ID des Arbeitsortes
    name: str     # Name des Arbeitsortes
    address: UUID # Referenz zur Adresse
```

### Appointment
```python
class Appointment(pydantic.BaseModel):
    id: UUID                          # Eindeutige ID des Termins
    plan_period_id: UUID             # Referenz zur Planungsperiode
    date: datetime.date              # Datum des Termins
    start_time: datetime.time        # Startzeit
    delta: datetime.timedelta        # Dauer des Termins
    location_id: UUID                # Referenz zum Arbeitsort
    person_ids: list[UUID]           # Liste der teilnehmenden Personen
    guests: pydantic.Json[list[str]] # Liste der Gäste
    notes: str                       # Notizen zum Termin
```

### Plan
```python
class Plan(pydantic.BaseModel):
    id: UUID                # Eindeutige ID des Plans
    name: str              # Name des Plans
    notes: str = ''        # Optionale Notizen
    plan_period_id: UUID   # Referenz zur Planungsperiode
    appointment_ids: list[UUID] # Liste der zugehörigen Termine
```
