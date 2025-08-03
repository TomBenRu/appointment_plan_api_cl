# Tech Stack - appointment_plan_api_cl

## Backend-Framework
- **FastAPI** >= 0.104.1 - Modernes Python Web-Framework
- **Uvicorn** >= 0.24.0 - ASGI Server für FastAPI
- **Python** >= 3.12 - Moderne Python-Version

## Datenbank & ORM
- **PonyORM** >= 0.7.16 - Object-Relational Mapping
- **SQLite** - Entwicklungsdatenbank (data/appointments.sqlite)
- **PostgreSQL** - Produktionsdatenbank (via DATABASE_URL)

## Frontend-Stack
- **Jinja2** >= 3.1.2 - Template-Engine für HTML
- **Tailwind CSS** - CSS-Framework für Styling
- **Alpine.js** - Leichtgewichtiges JavaScript-Framework
- **HTMX** - Für moderne Webinteraktionen ohne JavaScript

## Authentication & Security
- **Python-JOSE** - JWT Token-Handling
- **Passlib[bcrypt]** >= 1.7.4 - Password Hashing
- **Email-Validator** >= 2.1.0 - E-Mail-Validierung
- **Python-Multipart** >= 0.0.6 - Multipart Form-Handling

## Data Validation
- **Pydantic** >= 2.4.2 - Data Validation und Serialization

## Development Tools
- **pytest** >= 7.4.0 - Testing Framework
- **pytest-cov** >= 4.1.0 - Test Coverage
- **black** >= 23.7.0 - Code Formatter (Zeilen-Länge: 100)
- **isort** >= 5.12.0 - Import Sorter (black-kompatibel)
- **mypy** >= 1.5.1 - Type Checker

## Package Management
- **uv** - Moderner Python Package Manager (uv.lock vorhanden)
- **pyproject.toml** - Projektdefinition und Tool-Konfiguration

## Architektur-Pattern
- **Service Layer Pattern** - Business Logic in Services
- **Repository Pattern** - Datenzugriff über PonyORM
- **Exception-Driven Development** - Strukturierte Error-Handling
- **Middleware Pattern** - Error-Handling und Debugging
