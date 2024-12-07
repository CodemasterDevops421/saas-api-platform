from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import gzip

class CompressionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, minimum_size: int = 500):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if 'gzip' in request.headers.get('Accept-Encoding', ''):
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            
            response.body = gzip.compress(
                response.body,
                compresslevel=6
            )

        return response

class ETagMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if request.method in ['GET', 'HEAD']:
            etag = f'"{hash(response.body)}"'
            response.headers['ETag'] = etag
            
            if request.headers.get('If-None-Match') == etag:
                return Response(status_code=304)
        
        return response