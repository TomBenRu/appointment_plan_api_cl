from enum import Enum

class Role(str, Enum):
    """Benutzerrollen im System."""
    GUEST = "guest"
    APPRENTICE = "apprentice"
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
            cls.APPRENTICE: 2,
            cls.EMPLOYEE: 3,
            cls.DISPATCHER: 4,
            cls.ADMIN: 5,
            cls.SUPERVISOR: 6
        }
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
