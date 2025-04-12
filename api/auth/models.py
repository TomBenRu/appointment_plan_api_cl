from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import datetime

from api.auth.roles import Role

class Token(BaseModel):
    """Token-Antwortmodell für OAuth2."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Payload-Daten des JWT-Tokens."""
    username: Optional[str] = None
    person_id: Optional[UUID4] = None
    role: Optional[Role] = None
    exp: Optional[datetime] = None

class UserBase(BaseModel):
    """Basismodell für Benutzer."""
    username: str

class UserCreate(UserBase):
    """Modell zur Erstellung eines Benutzers."""
    password: str
    person_id: UUID4
    role: Role = Role.EMPLOYEE

class UserInDB(UserBase):
    """Modell für einen Benutzer wie er in der Datenbank gespeichert ist."""
    hashed_password: str
    person_id: UUID4
    role: Role
    disabled: bool = False

class User(UserBase):
    """Modell für einen Benutzer in der Anwendung."""
    person_id: UUID4
    role: Role
    disabled: bool = False
