from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.api_key import ApiKey, ApiKeyStatus
from ..core.security import generate_api_key
from ..core.exceptions import ValidationError

class ApiKeyService:
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: int,
        name: str,
        expiration_days: Optional[int] = 365,
        permissions: Optional[dict] = None
    ) -> ApiKey:
        existing_keys = db.query(ApiKey).filter(
            ApiKey.user_id == user_id,
            ApiKey.status == ApiKeyStatus.ACTIVE
        ).count()
        
        if existing_keys >= 5:
            raise ValidationError("Maximum number of active API keys reached")

        expiration_date = None
        if expiration_days:
            expiration_date = datetime.utcnow() + timedelta(days=expiration_days)

        api_key = ApiKey(
            user_id=user_id,
            key=generate_api_key(),
            name=name,
            expiration_date=expiration_date,
            permissions=permissions or {}
        )

        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key

    @staticmethod
    def get_user_api_keys(db: Session, user_id: int) -> List[ApiKey]:
        return db.query(ApiKey).filter(
            ApiKey.user_id == user_id,
            ApiKey.status == ApiKeyStatus.ACTIVE
        ).all()

    @staticmethod
    def revoke_api_key(db: Session, key_id: int, user_id: int) -> bool:
        api_key = db.query(ApiKey).filter(
            ApiKey.id == key_id,
            ApiKey.user_id == user_id
        ).first()

        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")

        api_key.status = ApiKeyStatus.REVOKED
        db.commit()
        return True

    @staticmethod
    def validate_api_key(db: Session, key: str) -> Optional[ApiKey]:
        api_key = db.query(ApiKey).filter(
            ApiKey.key == key,
            ApiKey.status == ApiKeyStatus.ACTIVE
        ).first()

        if not api_key or not api_key.is_valid():
            return None

        api_key.last_used_at = datetime.utcnow()
        db.commit()
        return api_key

    @staticmethod
    def check_permissions(api_key: ApiKey, required_permission: str) -> bool:
        if not api_key.permissions:
            return False
        return required_permission in api_key.permissions.get('scopes', [])