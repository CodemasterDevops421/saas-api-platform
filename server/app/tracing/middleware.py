from fastapi import Request
from opentelemetry import trace
from typing import Optional

class TracingMiddleware:
    async def __call__(self, request: Request, call_next):
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span(
            "http_request",
            attributes={
                "http.method": request.method,
                "http.url": str(request.url),
                "http.client_ip": request.client.host
            }
        ) as span:
            try:
                response = await call_next(request)
                span.set_attribute("http.status_code", response.status_code)
                return response
            except Exception as e:
                span.set_attribute("error", str(e))
                raise