from enum import Enum

class Role(str, Enum):
    """Benutzerrollen im System."""
    GUEST = "guest"
    EMPLOYEE = "employee"
    DISPATCHER = "dispatcher"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    
    @classmethod
    def has_permission(cls, required_role: "Role", user_role: "Role") -> bool:
        """
        Prüft, ob eine Benutzerrolle die erforderlichen Berechtigungen hat.
        Höhere Rollen haben automatisch die Berechtigungen niedrigerer Rollen.
        """
        role_hierarchy = {
            cls.GUEST: 1,
            cls.EMPLOYEE: 2,
            cls.DISPATCHER: 3,
            cls.ADMIN: 4,
            cls.SUPERVISOR: 5
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
