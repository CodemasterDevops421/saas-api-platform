from collections import defaultdict
from typing import List, Dict, Any
from asyncio import Lock, gather
import time

class BatchRequestHandler:
    def __init__(self, batch_size: int = 100, max_wait_ms: int = 50):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.batches = defaultdict(list)
        self.locks = defaultdict(Lock)
        
    async def add_to_batch(self, operation: str, item: Any) -> Any:
        async with self.locks[operation]:
            batch = self.batches[operation]
            batch.append(item)
            
            if len(batch) >= self.batch_size:
                return await self._process_batch(operation)
                
            if batch and time.time() - batch[0]['timestamp'] > self.max_wait_ms / 1000:
                return await self._process_batch(operation)
                
        return None
    
    async def _process_batch(self, operation: str) -> List[Dict]:
        batch = self.batches[operation]
        self.batches[operation] = []
        
        if not batch:
            return []
            
        try:
            results = await self._execute_batch(operation, batch)
            return results
        except Exception as e:
            # Split batch and retry on failure
            if len(batch) > 1:
                mid = len(batch) // 2
                self.batches[operation] = batch[mid:]
                return await self._process_batch(operation)
            raise e
    
    async def _execute_batch(self, operation: str, items: List[Dict]) -> List[Dict]:
        if operation == "db_insert":
            return await self._batch_db_insert(items)
        elif operation == "cache_update":
            return await self._batch_cache_update(items)
        return []