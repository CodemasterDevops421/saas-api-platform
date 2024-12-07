from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password, verify_password_strength
from redis import Redis
from ..core.config import settings
import time

redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)

def check_login_attempts(email: str) -> bool:
    key = f"login_attempts:{email}"
    attempts = redis_client.get(key)
    if attempts and int(attempts) >= settings.MAX_LOGIN_ATTEMPTS:
        return False
    return True

def record_login_attempt(email: str, success: bool):
    key = f"login_attempts:{email}"
    if success:
        redis_client.delete(key)
    else:
        redis_client.incr(key)
        redis_client.expire(key, settings.LOGIN_ATTEMPTS_WINDOW * 60)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    if not verify_password_strength(user.password):
        raise HTTPException(status_code=400, detail="Password does not meet security requirements")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def authenticate(db: Session, email: str, password: str):
    if not check_login_attempts(email):
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {settings.LOGIN_ATTEMPTS_WINDOW} minutes"
        )
    
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        record_login_attempt(email, False)
        return None
    
    record_login_attempt(email, True)
    return user