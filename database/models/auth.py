from uuid import UUID
import datetime

from pony.orm import Required, Optional as PonyOptional, PrimaryKey

from .base import db

class User(db.Entity):
    """
    Benutzermodell für die Authentifizierung und Autorisierung.
    """
    id = PrimaryKey(UUID, auto=True)
    username = Required(str, unique=True)
    hashed_password = Required(str)
    person = Required('Person', reverse='auth_user')
    role = Required(str)
    disabled = Required(bool, default=False)
