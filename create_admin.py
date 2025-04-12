"""
Dieses Skript erstellt einen neuen Admin-Benutzer in der Datenbank.
"""
from uuid import UUID
import sys
import getpass

from pony.orm import db_session, commit

from database import setup_database
from database.models import User, Person
from api.auth import get_password_hash
from api.auth.roles import Role

@db_session
def create_admin_user(username: str, password: str, person_id: UUID):
    """
    Erstellt einen neuen Administrator-Benutzer.
    
    Args:
        username: Der Benutzername
        password: Das Passwort
        person_id: Die ID der Person, mit der der Benutzer verknüpft wird
    """
    # Prüfen, ob der Benutzername bereits existiert
    if User.get(username=username):
        print(f"Ein Benutzer mit dem Namen '{username}' existiert bereits.")
        return False
    
    # Prüfen, ob die Person existiert
    person = Person.get(id=person_id)
    if not person:
        print(f"Person mit ID '{person_id}' nicht gefunden.")
        return False
    
    # Passwort hashen
    hashed_password = get_password_hash(password)
    
    # Benutzer erstellen
    User(
        username=username,
        hashed_password=hashed_password,
        person=person,
        role=Role.ADMIN.value,
        disabled=False
    )
    commit()
    
    print(f"Admin-Benutzer '{username}' erfolgreich erstellt und mit Person '{person.f_name} {person.l_name}' verknüpft.")
    return True

if __name__ == "__main__":
    # Datenbank einrichten
    setup_database()
    
    print("=== Admin-Benutzer erstellen ===")
    
    # Benutzername abfragen
    username = input("Benutzername: ")
    
    # Passwort abfragen (wird nicht angezeigt)
    password = getpass.getpass("Passwort: ")
    
    # Personen-ID abfragen
    person_id_str = input("Personen-ID (UUID): ")
    try:
        person_id = UUID(person_id_str)
    except ValueError:
        print("Ungültige UUID-Format.")
        sys.exit(1)
    
    # Admin-Benutzer erstellen
    if create_admin_user(username, password, person_id):
        print("Admin-Benutzer erfolgreich erstellt.")
    else:
        print("Fehler beim Erstellen des Admin-Benutzers.")
        sys.exit(1)
