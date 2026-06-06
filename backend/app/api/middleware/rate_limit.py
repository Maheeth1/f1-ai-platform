import time
from functools import wraps
from fastapi import Request, HTTPException, status
from app.services.cache_service import CacheService

def rate_limit(requests: int = 100, window: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                return await func(*args, **kwargs) if __import__("asyncio").iscoroutinefunction(func) else func(*args, **kwargs)
                
            client = CacheService.get_client()
            if not client:
                # Fail open if Redis is down
                return await func(*args, **kwargs) if __import__("asyncio").iscoroutinefunction(func) else func(*args, **kwargs)
                
            # Use client IP as identifier
            client_ip = request.client.host if request.client else "unknown"
            key = f"rate_limit:{client_ip}:{request.url.path}"
            
            now = time.time()
            window_start = now - window
            
            pipeline = client.pipeline()
            # Remove old requests
            pipeline.zremrangebyscore(key, 0, window_start)
            # Count requests in window
            pipeline.zcard(key)
            # Add current request
            pipeline.zadd(key, {str(now): now})
            # Set expiry
            pipeline.expire(key, window)
            
            results = pipeline.execute()
            request_count = results[1]
            
            if request_count >= requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests, please try again later."
                )
                
            import inspect
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        return wrapper
    return decorator
