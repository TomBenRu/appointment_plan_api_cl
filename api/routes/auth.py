from datetime import timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pony.orm import db_session, commit

from api.auth import (
    authenticate_user, create_access_token, get_password_hash,
    Token, User, UserCreate, Role, require_admin, require_employee
)
from database.models import User as DBUser, Person as DBPerson

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint zum Abrufen eines Access-Tokens.
    
    Args:
        form_data: Die Anmeldedaten (Benutzername und Passwort)
        
    Returns:
        Ein Token-Objekt mit Access-Token und Token-Typ
        
    Raises:
        HTTPException: Bei ungültigen Anmeldeinformationen
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value, "person_id": str(user.person_id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
@db_session
async def register_user(user_data: UserCreate, current_user: User = Depends(require_admin)):
    """
    Registriert einen neuen Benutzer.
    Nur Administratoren können neue Benutzer registrieren.
    
    Args:
        user_data: Die Daten des neuen Benutzers
        current_user: Der aktuelle Benutzer (muss Admin sein)
        
    Returns:
        Das erstellte User-Objekt
        
    Raises:
        HTTPException: Bei Validierungsfehlern
    """
    # Prüfen, ob der Benutzername bereits existiert
    if DBUser.get(username=user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzername bereits registriert"
        )
    
    # Prüfen, ob die Person existiert
    person = DBPerson.get(id=user_data.person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person nicht gefunden"
        )
    
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
    commit()
    
    return User(
        username=new_user.username,
        person_id=new_user.person.id,
        role=Role(new_user.role),
        disabled=new_user.disabled
    )

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(require_employee)):
    """
    Gibt den aktuellen Benutzer zurück.
    
    Args:
        current_user: Der aktuelle Benutzer
        
    Returns:
        Das User-Objekt des aktuellen Benutzers
    """
    return current_user
