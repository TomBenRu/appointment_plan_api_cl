from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import (
    authenticate_user, create_access_token,
    Token, User, UserCreate, require_admin, require_employee
)
from api.services import AuthService
from api.exceptions.auth import AuthenticationException

router = APIRouter()

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint zum Abrufen eines Access-Tokens.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthenticationException(
            message="Ungültiger Benutzername oder Passwort",
            details={"username": form_data.username}
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value, "person_id": str(user.person_id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=User)
def register_user(user_data: UserCreate, current_user: User = Depends(require_admin)):
    """
    Registriert einen neuen Benutzer.
    Nur Administratoren können neue Benutzer registrieren.
    """
    return AuthService.create_user(user_data)

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(require_employee)):
    """
    Gibt den aktuellen Benutzer zurück.
    """
    return current_user
