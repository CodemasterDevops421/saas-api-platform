from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User, UserStatus
from ..schemas.user import UserCreate, UserUpdate
from ..core.security import get_password_hash, verify_password
from datetime import datetime

class UserService:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        if UserService.get_user_by_email(db, user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        db_user = User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            full_name=user.full_name,
            status=UserStatus.ACTIVE
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_user(db, user_id)
        if not user:
            return False
        
        user.status = UserStatus.INACTIVE
        user.is_active = False
        db.commit()
        return True

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_user_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
            
        user.last_login = datetime.utcnow()
        db.commit()
        return user