"""
Service für Authentifizierung und Benutzerverwaltung.
"""
from typing import Optional
from uuid import UUID

from pony.orm import db_session, ObjectNotFound

from api.auth import get_password_hash
from api.auth.models import User, UserCreate, UserInDB
from api.auth.roles import Role
from database.models import User as DBUser, Person as DBPerson
from api.exceptions.auth import (
    UserNotFoundException,
    DuplicateUsernameException,
    PersonNotFoundException
)

class AuthService:
    @staticmethod
    @db_session
    def get_user_by_username(username: str) -> Optional[UserInDB]:
        """
        Holt einen Benutzer aus der Datenbank.
        
        Args:
            username: Der Benutzername
            
        Returns:
            Ein UserInDB-Objekt, wenn der Benutzer gefunden wurde, sonst None
        """
        db_user = DBUser.get(username=username)
        if db_user:
            return UserInDB(
                username=db_user.username,
                hashed_password=db_user.hashed_password,
                person_id=db_user.person.id,
                role=Role(db_user.role),
                disabled=db_user.disabled
            )
        return None

    @staticmethod
    @db_session
    def create_user(user_data: UserCreate) -> User:
        """
        Erstellt einen neuen Benutzer.
        
        Args:
            user_data: Die Daten des neuen Benutzers
            
        Returns:
            Das erstellte User-Objekt
            
        Raises:
            DuplicateUsernameException: Wenn der Benutzername bereits existiert
            PersonNotFoundException: Wenn die zugehörige Person nicht gefunden wurde
        """
        # Prüfen, ob der Benutzername bereits existiert
        if DBUser.get(username=user_data.username):
            raise DuplicateUsernameException(username=user_data.username)
        
        # Prüfen, ob die Person existiert
        try:
            person = DBPerson.get(id=user_data.person_id)
            if not person:
                raise PersonNotFoundException(person_id=user_data.person_id)
        except ObjectNotFound:
            raise PersonNotFoundException(person_id=user_data.person_id)
        
        # Hashen des Passworts
        hashed_password = get_password_hash(user_data.password)
        
        # Benutzer erstellen
        new_user = DBUser(
            username=user_data.username,
            hashed_password=hashed_password,
            person=person,
            role=user_data.role.value,
            disabled=False
        )
        
        return User(
            username=new_user.username,
            person_id=new_user.person.id,
            role=Role(new_user.role),
            disabled=new_user.disabled
        )