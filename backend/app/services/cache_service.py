import redis
import json
from typing import Any, Optional
from app.core.config import settings
from app.core.logger import logger

class CacheService:
    _client = None
    
    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._client is None:
            try:
                cls._client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
                # Ping to check connection
                cls._client.ping()
                logger.info(f"Connected to Redis at {settings.redis_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Caching will be disabled.")
                cls._client = None
        return cls._client

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        client = cls.get_client()
        if not client:
            return None
            
        try:
            val = client.get(key)
            if val:
                return json.loads(val)
            return None
        except Exception as e:
            logger.warning(f"Redis GET failed for {key}: {e}")
            return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 3600) -> bool:
        client = cls.get_client()
        if not client:
            return False
            
        try:
            val_str = json.dumps(value)
            client.setex(key, ttl, val_str)
            return True
        except Exception as e:
            logger.warning(f"Redis SET failed for {key}: {e}")
            return False

    @classmethod
    def increment_hit(cls):
        client = cls.get_client()
        if client:
            try:
                client.incr("metrics:cache_hits")
            except:
                pass

    @classmethod
    def increment_miss(cls):
        client = cls.get_client()
        if client:
            try:
                client.incr("metrics:cache_misses")
            except:
                pass

    @classmethod
    def get_metrics(cls) -> dict:
        client = cls.get_client()
        if not client:
            return {"status": "offline", "hits": 0, "misses": 0, "hit_ratio": 0.0}
            
        try:
            hits = int(client.get("metrics:cache_hits") or 0)
            misses = int(client.get("metrics:cache_misses") or 0)
            total = hits + misses
            hit_ratio = round((hits / total) * 100, 2) if total > 0 else 0.0
            return {
                "status": "online",
                "hits": hits,
                "misses": misses,
                "hit_ratio": hit_ratio
            }
        except Exception:
            return {"status": "error", "hits": 0, "misses": 0, "hit_ratio": 0.0}
