from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, billing, analytics, api_keys
from .core.config import settings
from .middleware.analytics import analytics_middleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware('http')(analytics_middleware)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(api_keys.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to SaaS API Platform"}