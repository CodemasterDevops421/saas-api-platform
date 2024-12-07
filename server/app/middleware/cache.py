from fastapi import Request, Response
from ..core.cache_manager import CacheManager
from typing import Optional
import hashlib

class CacheMiddleware:
    def __init__(self, cache: CacheManager):
        self.cache = cache

    async def __call__(self, request: Request, call_next):
        if request.method != 'GET':
            return await call_next(request)

        cache_key = self._generate_cache_key(request)
        cached_response = await self.cache.get(cache_key)

        if cached_response:
            return Response(
                content=cached_response['content'],
                status_code=cached_response['status_code'],
                headers=cached_response['headers']
            )

        response = await call_next(request)
        
        if 200 <= response.status_code < 400:
            await self.cache.set(
                cache_key,
                {
                    'content': response.body,
                    'status_code': response.status_code,
                    'headers': dict(response.headers)
                }
            )

        return response

    def _generate_cache_key(self, request: Request) -> str:
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items())),
            request.headers.get('accept', ''),
            request.headers.get('accept-encoding', '')
        ]
        return hashlib.sha256('|'.join(key_parts).encode()).hexdigest()