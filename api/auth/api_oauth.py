from typing import List, Optional, Callable, Type

from fastapi import Depends, HTTPException, status

from api.auth.oauth2 import get_current_active_user
from api.auth.models import User
from api.auth.roles import Role

class RoleChecker:
    """
    Überprüft, ob ein Benutzer die erforderlichen Rollen hat.
    """
    def __init__(self, required_role: Role):
        self.required_role = required_role
    
    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        """
        Überprüft, ob der Benutzer die erforderliche Rolle hat.
        
        Args:
            user: Der zu überprüfende Benutzer
            
        Returns:
            Das Benutzer-Objekt, wenn die Autorisierung erfolgreich ist
            
        Raises:
            HTTPException: Wenn der Benutzer nicht die erforderliche Rolle hat
        """
        if not Role.has_permission(self.required_role, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Nicht genügend Berechtigungen. Rolle {user.role} hat keine Berechtigung für {self.required_role}.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

# Vordefinierte Abhängigkeiten für verschiedene Rollenstufen
require_employee = RoleChecker(Role.EMPLOYEE)
require_dispatcher = RoleChecker(Role.DISPATCHER)
require_admin = RoleChecker(Role.ADMIN)
require_supervisor = RoleChecker(Role.SUPERVISOR)
allow_guest = RoleChecker(Role.GUEST)
