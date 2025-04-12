import os
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pony.orm import db_session

from api.auth.models import TokenData, User, UserInDB
from api.auth.roles import Role
from database.models.auth import User as DBUser
from database.models.entities import Person as DBPerson

# Konfigurationsvariablen
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Passwort-Hashing-Kontext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2-Schema für die Token-Extraktion
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Überprüft, ob ein Klartext-Passwort zu einem Hash passt.
    
    Args:
        plain_password: Das Klartext-Passwort
        hashed_password: Der gespeicherte Passwort-Hash
        
    Returns:
        True, wenn das Passwort übereinstimmt, sonst False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generiert einen Hash für ein Passwort.
    
    Args:
        password: Das zu hashende Passwort
        
    Returns:
        Der generierte Passwort-Hash
    """
    return pwd_context.hash(password)

@db_session
def get_user(username: str) -> Optional[UserInDB]:
    """
    Holt einen Benutzer aus der Datenbank.
    
    Args:
        username: Der Benutzername
        
    Returns:
        Ein UserInDB-Objekt, wenn der Benutzer gefunden wurde, sonst None
    """
    db_user = DBUser.get(username=username)
    if db_user:
        user_dict = {
            "username": db_user.username,
            "hashed_password": db_user.hashed_password,
            "person_id": db_user.person.id,
            "role": Role(db_user.role),
            "disabled": db_user.disabled
        }
        return UserInDB(**user_dict)
    return None

@db_session
def authenticate_user(username: str, password: str) -> Union[User, bool]:
    """
    Authentifiziert einen Benutzer anhand von Benutzername und Passwort.
    
    Args:
        username: Der Benutzername
        password: Das Passwort
        
    Returns:
        Ein User-Objekt bei erfolgreicher Authentifizierung, sonst False
    """
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return User(
        username=user.username,
        person_id=user.person_id,
        role=user.role,
        disabled=user.disabled
    )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Erstellt ein JWT-Access-Token.
    
    Args:
        data: Die Daten, die im Token gespeichert werden sollen
        expires_delta: Optional. Die Gültigkeitsdauer des Tokens
        
    Returns:
        Das kodierte JWT-Token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Ermittelt den aktuellen Benutzer anhand des JWT-Tokens.
    
    Args:
        token: Das JWT-Token
        
    Returns:
        Ein User-Objekt des aktuellen Benutzers
        
    Raises:
        HTTPException: Wenn das Token ungültig ist oder der Benutzer nicht gefunden wird
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ungültige Anmeldeinformationen",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        role_str: str = payload.get("role")
        person_id: str = payload.get("person_id")
        token_data = TokenData(username=username, role=Role(role_str) if role_str else None, person_id=person_id)
    except JWTError:
        raise credentials_exception
    
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        username=user.username,
        person_id=user.person_id,
        role=user.role,
        disabled=user.disabled
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Prüft, ob der aktuelle Benutzer aktiv ist.
    
    Args:
        current_user: Der aktuelle Benutzer
        
    Returns:
        Das User-Objekt des aktuellen Benutzers
        
    Raises:
        HTTPException: Wenn der Benutzer deaktiviert ist
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inaktiver Benutzer")
    return current_user
