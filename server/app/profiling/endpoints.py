from fastapi import APIRouter, Depends
from ..core.auth import get_current_admin_user
from .profiler import Profiler
from .memory_tracker import MemoryTracker

router = APIRouter(prefix="/profiling", tags=["profiling"])

@router.get("/memory")
async def get_memory_stats(user = Depends(get_current_admin_user)):
    tracker = MemoryTracker()
    tracker.start()
    
    stats = {
        'current': tracemalloc.get_traced_memory(),
        'peak': tracemalloc.get_tracemalloc_memory(),
        'traces': tracemalloc.get_object_traceback()
    }
    
    tracemalloc.stop()
    return stats

@router.get("/cpu")
async def get_cpu_profile(user = Depends(get_current_admin_user)):
    profiler = Profiler()
    stats = profiler.get_stats()
    return {
        'calls': stats.total_calls,
        'primitive_calls': stats.prim_calls,
        'total_time': stats.total_tt,
        'top_functions': stats.stats
    }