import tracemalloc
from fastapi import Request
from typing import Optional
from ..monitoring.logger import logger

class MemoryTracker:
    def __init__(self):
        self.snapshot = None
    
    def start(self):
        tracemalloc.start()
    
    def take_snapshot(self):
        if tracemalloc.is_tracing():
            self.snapshot = tracemalloc.take_snapshot()
    
    def compare_snapshots(self):
        if not self.snapshot:
            return
        
        current = tracemalloc.take_snapshot()
        stats = current.compare_to(self.snapshot, 'lineno')
        
        for stat in stats[:10]:
            logger.info("%s memory blocks: %.1f KiB",
                stat.traceback[0], stat.size / 1024)

def track_memory(func):
    tracker = MemoryTracker()
    
    async def wrapper(*args, **kwargs):
        tracker.start()
        tracker.take_snapshot()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            tracker.compare_snapshots()
            tracemalloc.stop()
    
    return wrapper