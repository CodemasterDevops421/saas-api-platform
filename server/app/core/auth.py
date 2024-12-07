from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from .exceptions import AuthenticationError
from .config import settings
from ..db.session import get_db
from ..services import user_service, jwt_service
from ..models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/{settings.API_V1_STR}/auth/login"
)

def get_token_payload(token: str) -> dict:
    try:
        return jwt_service.decode_token(token)
    except JWTError:
        raise AuthenticationError("Invalid token")

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = get_token_payload(token)
    email = payload.get("sub")
    if not email:
        raise AuthenticationError("Invalid token payload")

    user = user_service.get_user_by_email(db, email=email)
    if not user:
        raise AuthenticationError("User not found")

    # Check if token is in blocklist (for logout)
    if await jwt_service.is_token_blocked(token):
        raise AuthenticationError("Token has been revoked")

    # Store user in request state for audit logs
    request.state.user = user
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_superuser:
        raise AuthenticationError("Admin privileges required")
    return current_user