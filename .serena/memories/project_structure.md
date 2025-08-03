# Projektstruktur - appointment_plan_api_cl

## Root-Level Dateien
```
appointment_plan_api_cl/
├── main.py                 # FastAPI App Entry Point
├── create_admin.py         # Admin-User Creation Script
├── seed.py                 # Database Seeding Script
├── pyproject.toml          # Project Configuration
├── uv.lock                 # Dependency Lock File
├── README.md               # Project Documentation
└── planning.md             # Development Planning Notes
```

## API-Architektur
```
api/
├── __init__.py
├── templates.py            # Template Configuration
├── auth/                   # Authentication System
│   ├── __init__.py
│   ├── api_oauth.py        # API OAuth Implementation
│   ├── cookie_auth.py      # Cookie-based Authentication
│   ├── models.py           # Auth Data Models
│   ├── oauth2.py           # OAuth2 Implementation
│   └── roles.py            # User Role Management
├── exceptions/             # Domain-specific Exceptions
│   ├── __init__.py
│   ├── base.py             # Base Exception Classes
│   ├── appointment.py      # Appointment Exceptions
│   ├── auth.py             # Authentication Exceptions
│   ├── location.py         # Location Exceptions
│   ├── person.py           # Person Exceptions
│   └── plan.py             # Plan Exceptions
├── middleware/             # Cross-cutting Concerns
│   ├── __init__.py
│   ├── debug_route.py      # Debug Middleware
│   └── error_handler.py    # Global Error Handling
├── models/                 # Pydantic Schemas
│   ├── __init__.py
│   └── schemas.py          # API Data Schemas
├── routes/                 # Route Definitions
│   ├── __init__.py
│   ├── api/                # JSON API Endpoints
│   │   ├── __init__.py
│   │   ├── appointments.py # Appointment CRUD API
│   │   ├── auth.py         # Authentication API
│   │   ├── locations.py    # Location Management API
│   │   └── plans.py        # Plan Management API
│   └── web/                # HTML Rendering Routes
│       ├── __init__.py
│       ├── auth.py         # Web Authentication Routes
│       ├── calendar/       # Calendar Web Routes
│       │   ├── __init__.py
│       │   ├── calendar.py # Calendar Views
│       │   ├── locations.py # Location Views
│       │   ├── persons.py  # Person Views
│       │   ├── plans.py    # Plan Views
│       │   └── search.py   # Search Functionality
│       └── planning/       # Planning Web Routes
│           ├── __init__.py
│           ├── availability.py # Availability Management
│           ├── periods.py   # Period Management
│           ├── planning.py  # Planning Views
│           └── teams.py     # Team Management
├── services/               # Business Logic Layer
│   ├── __init__.py
│   ├── appointment_service.py # Appointment Business Logic
│   ├── auth_service.py     # Authentication Logic
│   ├── calendar_service.py # Calendar Logic
│   ├── location_service.py # Location Management
│   ├── person_service.py   # Person Management
│   └── plan_service.py     # Plan Management
└── utils/                  # Helper Functions
    ├── __init__.py
    ├── converters.py       # Data Converters
    └── menu_sections.py    # Menu Utilities
```

## Datenbank-Layer
```
database/
├── __init__.py
├── db_setup.py             # Database Configuration
└── models/                 # PonyORM Entity Definitions
    ├── __init__.py
    ├── base.py             # Database Instance
    ├── auth.py             # Authentication Entities
    └── entities.py         # Business Domain Entities
```

## Frontend-Assets
```
static/                     # Static Web Assets
└── css/                    # CSS Stylesheets

templates/                  # Jinja2 HTML Templates
```

## Data & Scripts
```
data/                       # Database Files
└── appointments.sqlite     # SQLite Development Database

scripts/                    # Utility Scripts
└── create_admin.py         # Admin User Creation

Dokumentation HCC Plan Online/ # Documentation
```

## Architektur-Prinzipien

### Layered Architecture
1. **Presentation Layer**: `api/routes/` (API & Web)
2. **Business Logic Layer**: `api/services/`
3. **Data Access Layer**: `database/models/`
4. **Cross-cutting Concerns**: `api/middleware/`, `api/exceptions/`

### Domain-Driven Design
- **Entities**: Person, Appointment, Location, Plan
- **Services**: Domain-specific Business Logic
- **Exceptions**: Domain-specific Error Handling

### Separation of Concerns
- **API vs Web Routes**: JSON vs HTML Responses
- **Auth Layer**: Separate Authentication Logic
- **Middleware**: Cross-cutting Concerns
- **Utils**: Reusable Helper Functions
