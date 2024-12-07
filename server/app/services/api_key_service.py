from sqlalchemy.orm import Session
from ..models.api_key import ApiKey
import secrets

def generate_api_key():
    return f"sk_{secrets.token_urlsafe(32)}"

async def create_api_key(db: Session, user_id: int, name: str):
    api_key = ApiKey(
        user_id=user_id,
        key=generate_api_key(),
        name=name
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key

async def get_user_api_keys(db: Session, user_id: int):
    return db.query(ApiKey).filter(ApiKey.user_id == user_id).all()

async def get_api_key(db: Session, key_id: int):
    return db.query(ApiKey).filter(ApiKey.id == key_id).first()

async def delete_api_key(db: Session, key_id: int):
    db.query(ApiKey).filter(ApiKey.id == key_id).delete()
    db.commit()