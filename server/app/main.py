from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, users, billing, analytics, api_keys
from .core.config import settings
from .middleware.monitoring import MonitoringMiddleware
from .middleware.security import SecurityMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .core.versioning import APIVersion, version_router

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        docs_url=f"/api/{APIVersion.V1}/docs",
        openapi_url=f"/api/{APIVersion.V1}/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SecurityMiddleware)
    app.add_middleware(MonitoringMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # Version 1 routes
    version_router(app, auth.router, APIVersion.V1)
    version_router(app, users.router, APIVersion.V1)
    version_router(app, billing.router, APIVersion.V1)
    version_router(app, analytics.router, APIVersion.V1)
    version_router(app, api_keys.router, APIVersion.V1)

    return app

app = create_application()