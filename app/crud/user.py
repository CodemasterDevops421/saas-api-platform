from sqlalchemy.orm import Session
from .. import models, schemas
from ..core.security import get_password_hash
import secrets
from datetime import datetime

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_api_key(db: Session, user_id: int, api_key: schemas.APIKeyCreate):
    db_api_key = models.APIKey(
        key=f"sk_{secrets.token_urlsafe(32)}",
        name=api_key.name,
        user_id=user_id,
        expires_at=api_key.expires_at
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    return db_api_key

def get_api_key_by_token(db: Session, api_key: str):
    return db.query(models.APIKey).filter(
        models.APIKey.key == api_key,
        models.APIKey.is_active == True
    ).first()