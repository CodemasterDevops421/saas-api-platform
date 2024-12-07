from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .... import crud, models, schemas
from ....database import get_db
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)

@router.post("/api-keys", response_model=schemas.APIKey)
def create_api_key(
    api_key: schemas.APIKeyCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_api_key(db=db, user_id=current_user.id, api_key=api_key)