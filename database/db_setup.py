import os
from pony.orm import db_session
from .models import db

def setup_database(database_url=None):
    """
    Konfiguriert die Datenbank-Verbindung.
    
    Args:
        database_url: Optional. Ein Database-URL-String. Wenn nicht angegeben,
                     wird die Umgebungsvariable DATABASE_URL verwendet, oder eine
                     SQLite-DB im Entwicklungsmodus erstellt.
    """
    if database_url is None:
        database_url = os.environ.get('DATABASE_URL')
    
    if database_url is None:
        # Entwicklungsmodus: SQLite-Datenbank verwenden
        db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, 'appointments.sqlite')
        db.bind(provider='sqlite', filename=db_path, create_db=True)
    else:
        # Produktionsmodus: PostgreSQL-Datenbank verwenden
        # Der URL sollte im Format postgresql://user:password@host:port/database sein
        db.bind(provider='postgres', dsn=database_url)
    
    # Datenbank-Schema erstellen (Tabellen, etc.)
    db.generate_mapping(create_tables=True)
    
    return db
