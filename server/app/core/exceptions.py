from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class APIError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Dict[str, str] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code

class AuthenticationError(APIError):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR"
        )

class RateLimitError(APIError):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_ERROR"
        )

class SubscriptionError(APIError):
    def __init__(self, detail: str = "Subscription error"):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=detail,
            error_code="SUBSCRIPTION_ERROR"
        )

class ValidationError(APIError):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )