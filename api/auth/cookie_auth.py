"""
Cookie-basierte Authentifizierung für Web-Routen.
"""
from typing import Optional
from fastapi import Request, HTTPException, status, Cookie, Depends
from jose import JWTError, jwt

from api.auth.oauth2 import SECRET_KEY, ALGORITHM
from api.auth.models import User, TokenData
from api.auth.roles import Role
from api.auth import get_user
from api.exceptions.auth import AuthenticationException

async def get_token_from_cookie(
    request: Request,
    access_token: Optional[str] = Cookie(None, alias="appointments_token")
) -> Optional[str]:
    """
    Extrahiert das JWT-Token aus dem Cookie.
    """
    if access_token:
        return access_token
    return None

async def get_current_user_from_cookie(token: Optional[str] = Depends(get_token_from_cookie)) -> Optional[User]:
    """
    Ermittelt den aktuellen Benutzer anhand des Cookies.
    """
    if token is None:
        return None
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
            
        role_str: str = payload.get("role")
        person_id: str = payload.get("person_id")
        token_data = TokenData(username=username, role=Role(role_str) if role_str else None, person_id=person_id)
        
        user = get_user(token_data.username)
        if user is None or user.disabled:
            return None
        
        result_user = User(
            username=user.username,
            person_id=user.person_id,
            role=user.role,
            disabled=user.disabled
        )
        return result_user
        
    except Exception as e:
        return None

class WebRoleChecker:
    """
    Überprüft, ob ein Benutzer die erforderlichen Rollen hat.
    Wirft einen 401-Fehler, wenn die Authentifizierung/Autorisierung fehlschlägt.
    """
    def __init__(self, required_role: Role):
        self.required_role = required_role

    async def __call__(self, request: Request, user: Optional[User] = Depends(get_current_user_from_cookie)) -> User:

        # Information über die erforderliche Rolle in der Request speichern
        request.state.required_role = self.required_role

        # Authentifizierung prüfen
        if user is None:
            request.state.show_login_modal = True
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Anmeldung erforderlich"
            )
            
        # Autorisierung prüfen
        if not Role.has_permission(self.required_role, user.role):
            request.state.show_login_modal = True
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Unzureichende Berechtigungen. Rolle {user.role} hat keinen Zugriff auf {self.required_role}."
            )
        
        # Benutzer hat ausreichende Berechtigungen
        request.state.show_login_modal = False
        return user

# Vordefinierte Abhängigkeit für Web-Routen
require_web_guest = WebRoleChecker(Role.GUEST)
require_web_employee = WebRoleChecker(Role.EMPLOYEE)
require_web_dispatcher = WebRoleChecker(Role.DISPATCHER)
require_web_admin = WebRoleChecker(Role.ADMIN)
require_web_supervisor = WebRoleChecker(Role.SUPERVISOR)
