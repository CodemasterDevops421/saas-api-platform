from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exceptions import APIError
from ..monitoring.logger import logger

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    logger.error(
        "API error occurred",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "status": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Validation error",
        extra={
            "errors": str(exc),
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        }
    )