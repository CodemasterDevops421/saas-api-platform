from fastapi import FastAPI
from enum import Enum

class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"

def version_router(app: FastAPI, prefix: str, version: APIVersion):
    return app.include_router(
        prefix=f"/api/{version}/{prefix}",
        tags=[f"{prefix}-{version}"])