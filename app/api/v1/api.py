from fastapi import APIRouter
from .endpoints import users, payment, analytics

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])