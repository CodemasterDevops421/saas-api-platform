from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
import asyncio

@dataclass
class RateLimit:
    limit: int
    remaining: int
    reset: datetime

class RateLimiter:
    def __init__(self):
        self._locks: Dict[str, asyncio.Lock] = {}
        self._limits: Dict[str, RateLimit] = {}

    async def acquire(self, key: str, limit: int) -> Optional[RateLimit]:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            now = datetime.utcnow()
            rate = self._limits.get(key)

            if rate and rate.reset > now:
                if rate.remaining > 0:
                    rate.remaining -= 1
                    return rate
                return None

            self._limits[key] = RateLimit(
                limit=limit,
                remaining=limit - 1,
                reset=now.replace(minute=0, second=0, microsecond=0)
            )
            return self._limits[key]