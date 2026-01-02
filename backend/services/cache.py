import redis
from backend.core.config import settings
from typing import Optional

class CacheService:
    def __init__(self):
        # In a real app, you might want to handle connection errors gracefully
        # or use a connection pool
        try:
            self.r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.r = None

    def get(self, key: str) -> Optional[str]:
        if not self.r: return None
        try:
            return self.r.get(key)
        except:
            return None

    def set(self, key: str, value: str, ex: int = None):
        if not self.r: return
        try:
            self.r.set(key, value, ex=ex)
        except:
            pass

cache_service = CacheService()
