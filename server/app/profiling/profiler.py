import cProfile
import pstats
import io
from functools import wraps
from typing import Optional
from fastapi import Request
from ..core.config import settings

class Profiler:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and settings.PROFILING_ENABLED
        self.profiler = cProfile.Profile()
    
    def profile(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not self.enabled:
                return await func(*args, **kwargs)
            
            self.profiler.enable()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                self.profiler.disable()
                s = io.StringIO()
                ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
                ps.print_stats(20)
                print(s.getvalue())
        
        return wrapper

def profile_request(request: Request):
    profiler = Profiler()
    
    @profiler.profile
    async def process_request(request: Request):
        # Process request and measure performance
        pass
    
    return process_request(request)