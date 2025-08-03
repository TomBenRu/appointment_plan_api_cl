# Code Style & Konventionen - appointment_plan_api_cl

## Formatierung (Black)
- **Zeilenlänge**: 100 Zeichen (konfiguriert in pyproject.toml)
- **Target Version**: Python 3.12
- **Automatische Formatierung** mit black

## Import-Sortierung (isort)
- **Profil**: black-kompatibel
- **Zeilenlänge**: 100 Zeichen (konsistent mit black)
- **Automatische Import-Sortierung**

## Typ-Annotations
- **Vollständige Type Hints** für alle öffentlichen Funktionen
- **mypy**-kompatible Annotations
- **Pydantic** für Data Validation und Serialization
- **UUID** für Primärschlüssel statt Auto-Increment

## Naming Conventions
- **Snake_case** für Variablen und Funktionen
- **PascalCase** für Klassen
- **UPPER_CASE** für Konstanten
- **Beschreibende Namen** - z.B. `appointment_id` statt `id`

## Dokumentation
- **Docstrings** in deutscher Sprache
- **Args/Returns/Raises** Struktur für komplexe Funktionen
- **Inline-Kommentare** für komplexe Logik

## Service Layer Pattern
```python
class AppointmentService:
    @staticmethod
    @db_session
    def get_appointment_detail(appointment_id: UUID) -> schemas.AppointmentDetail:
        """
        Liefert Details zu einem bestimmten Termin.
        Args: appointment_id: Die UUID des gesuchten Termins
        Returns: Details zum Termin
        Raises: AppointmentNotFoundException: Wenn der Termin nicht gefunden wurde
        """
```

## Exception Handling
- **Strukturierte Custom Exceptions** pro Domäne
- **Service Layer** wirft Domain-spezifische Exceptions
- **Middleware** behandelt Exception-to-HTTP-Mapping

## Database Models (PonyORM)
- **UUID Primary Keys** statt Auto-Increment
- **Required/Optional** statt nullable
- **Utility Functions** wie `utcnow_naive()` für Timezone-Handling
- **Set-Beziehungen** für Many-to-Many

## Schema-Driven Development
- **Pydantic Schemas** für API Input/Output
- **Separate Schemas** für verschiedene Use Cases (Detail, List, Create, Update)
- **model_validate()** für ORM-zu-Schema Konvertierung

## Folder Structure Pattern
```
api/
├── auth/           # Authentication Logic
├── models/         # Pydantic Schemas
├── routes/         # API & Web Routes
│   ├── api/        # JSON API Endpoints
│   └── web/        # HTML Rendering Routes
├── services/       # Business Logic Layer
├── utils/          # Helper Functions
├── middleware/     # Cross-cutting Concerns
└── exceptions/     # Domain-specific Exceptions
```
