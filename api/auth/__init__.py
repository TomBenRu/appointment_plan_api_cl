from .roles import Role
from .models import User, UserCreate, UserInDB, Token, TokenData
from .oauth2 import (
    authenticate_user, create_access_token, 
    get_current_user, get_current_active_user, 
    get_password_hash, verify_password, get_user
)
from .api_oauth import (
    RoleChecker, require_employee, require_dispatcher,
    require_admin, require_supervisor, allow_guest
)
from .cookie_auth import (
    get_token_from_cookie, get_current_user_from_cookie,
    WebRoleChecker, require_web_guest, require_web_employee, require_web_dispatcher,
    require_web_admin, require_web_supervisor
)

__all__ = [
    'Role',
    'User', 'UserCreate', 'UserInDB', 'Token', 'TokenData',
    'authenticate_user', 'create_access_token',
    'get_current_user', 'get_current_active_user',
    'get_password_hash', 'verify_password', 'get_user',
    'RoleChecker', 'require_employee', 'require_dispatcher',
    'require_admin', 'require_supervisor', 'allow_guest',
    'get_token_from_cookie', 'get_current_user_from_cookie',
    'WebRoleChecker', 'require_web_guest', 'require_web_employee', 'require_web_dispatcher',
    'require_web_admin', 'require_web_supervisor'
]
