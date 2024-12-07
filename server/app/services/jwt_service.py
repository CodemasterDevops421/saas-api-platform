from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from ..core.config import settings

class JWTService:
    @staticmethod
    def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire})
        return jwt.encode(
            claims=to_encode,
            key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(
                token=token,
                key=settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")

    @staticmethod
    def verify_token(token: str) -> bool:
        try:
            decoded = jwt.decode(
                token=token,
                key=settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return datetime.fromtimestamp(decoded["exp"]) > datetime.utcnow()
        except JWTError:
            return False