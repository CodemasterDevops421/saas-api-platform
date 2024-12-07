from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .api.v1.api import api_router
from .database import create_db_and_tables

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()