# Entwicklungsrichtlinien - appointment_plan_api_cl

## Allgemeine Prinzipien

### Code-Qualität
- **Immer Type Hints verwenden** für öffentliche APIs
- **Docstrings in deutscher Sprache** für komplexe Funktionen
- **Beschreibende Variablennamen** bevorzugen
- **Single Responsibility Principle** befolgen

### Strukturelle Änderungen
⚠️ **WICHTIG**: Thomas bevorzugt **Absprache vor strukturellen Änderungen** an Architekturkomponenten
- Vor größeren Refactorings Rücksprache halten
- Bestehende Patterns und Konventionen respektieren
- Keine Breaking Changes ohne Diskussion

## Testing-Richtlinien

### Test-Strategie
- **Unit Tests** für Services-Layer
- **Integration Tests** für API-Endpoints
- **Coverage** mindestens 80% anstreben
- **pytest** als Testing-Framework

### Test-Struktur
```python
def test_appointment_service_get_detail():
    """Test für AppointmentService.get_appointment_detail()"""
    # Arrange
    # Act
    # Assert
```

## Datenbank-Entwicklung

### PonyORM Best Practices
- **@db_session** Decorator für alle DB-Operationen
- **UUID** als Primary Keys verwenden
- **utcnow_naive()** für Timestamp-Felder (Timezone-Kompatibilität)
- **Required/Optional** statt nullable
- **Repository Pattern** keine zusätzliche Repository-Layer implementieren

### Schema-Änderungen
- **Migrations** über PonyORM generate_mapping()
- **Backup** vor Schema-Änderungen erstellen
- **Development**: SQLite auto-create
- **Production**: PostgreSQL via DATABASE_URL

## API-Development

### Service-Layer Pattern
```python
class SomeService:
    @staticmethod
    @db_session
    def method_name(param: Type) -> ReturnType:
        """Beschreibung der Methode"""
        try:
            # Business Logic
            return result
        except SomeException:
            raise DomainSpecificException()
```

### Exception-Driven Development
- **Domain-spezifische Exceptions** in `api/exceptions/`
- **Service Layer** wirft Business Exceptions
- **Middleware** mapped zu HTTP-Status-Codes
- **Strukturierte Error Messages**

### Pydantic Schemas
- **Separate Schemas** für verschiedene Use Cases:
  - `CreateSchema` für Input
  - `UpdateSchema` für Partial Updates
  - `DetailSchema` für vollständige Ausgabe
  - `ListSchema` für Übersichten

## Frontend-Development

### Template-Driven Development
- **Jinja2** für HTML-Rendering
- **Tailwind CSS** für Styling
- **Alpine.js** für interaktive Elemente
- **HTMX** für AJAX-ähnliche Funktionalität

### Responsive Design
- **Mobile-First** Approach
- **Tailwind Breakpoints** verwenden
- **Accessibility** berücksichtigen

## Git-Workflow

### Commit-Messages
```
feat: neue Funktion hinzugefügt
fix: Bug in AppointmentService behoben
docs: README aktualisiert
refactor: Service-Layer umstrukturiert
test: Tests für Calendar-Service hinzugefügt
```

### Branch-Strategy
- **main** - Produktionsreifer Code
- **feature/feature-name** - Neue Features
- **bugfix/issue-description** - Bug-Fixes

## Deployment-Richtlinien

### Development
- **SQLite** lokale Entwicklung
- **python main.py** für lokalen Server
- **uvicorn --reload** für Auto-Reload

### Production
- **PostgreSQL** via DATABASE_URL
- **uvicorn** ohne --reload
- **Environment Variables** für Konfiguration

## Performance-Considerations

### Database
- **@db_session** für Transaktions-Grenzen
- **Lazy Loading** wo möglich
- **select()** für komplexe Queries

### API
- **Pydantic Validation** für Input
- **Exception Handling** für Error Cases
- **Middleware** für Cross-cutting Concerns

## Security-Guidelines

### Authentication
- **Bcrypt** für Password Hashing
- **JWT** für Session Management
- **Role-based** Access Control

### Data Validation
- **Pydantic** für Input Validation
- **UUID** statt Sequential IDs
- **CORS** Configuration für Production

## Troubleshooting

### Häufige Probleme
1. **PonyORM Database Lock**: db_session korrekt verwenden
2. **Import Cycles**: Service-Layer-Dependencies prüfen
3. **Template Not Found**: Jinja2-Konfiguration in api/templates.py
4. **Static Files**: mount in main.py konfiguriert

### Debug-Tools
- **FastAPI /docs** für API-Testing
- **PonyORM db.generate_mapping(create_tables=True)** für Schema-Updates
- **Middleware Debug Routes** für Request-Tracing
