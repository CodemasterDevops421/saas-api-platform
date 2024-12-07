from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..core.exceptions import AuthenticationError
from ..services import user_service, jwt_service
from ..schemas.auth import Token, TokenData
from datetime import timedelta
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = user_service.authenticate(
        db,
        email=form_data.username,
        password=form_data.password
    )
    if not user:
        raise AuthenticationError("Invalid credentials")

    access_token = jwt_service.create_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = jwt_service.create_token(
        data={"sub": user.email, "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    # Set refresh token in HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    response: Response,
    refresh_token: str = Depends(jwt_service.get_refresh_token),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt_service.decode_token(refresh_token)
        email = payload.get("sub")
        token_type = payload.get("type")

        if not email or token_type != "refresh":
            raise AuthenticationError("Invalid refresh token")

        user = user_service.get_user_by_email(db, email=email)
        if not user:
            raise AuthenticationError("User not found")

        # Generate new tokens
        access_token = jwt_service.create_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        new_refresh_token = jwt_service.create_token(
            data={"sub": user.email, "type": "refresh"},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # Set new refresh token in cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise AuthenticationError("Invalid refresh token")

@router.post("/logout")
async def logout(
    response: Response,
    token: str = Depends(jwt_service.get_current_token)
):
    # Add token to blocklist
    await jwt_service.block_token(token)
    
    # Clear refresh token cookie
    response.delete_cookie("refresh_token")
    
    return {"message": "Successfully logged out"}