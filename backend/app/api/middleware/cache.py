import hashlib
import json
from functools import wraps
from typing import Callable, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from app.services.cache_service import CacheService

def cached(ttl: int = 3600):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request object
            request: Request = kwargs.get("request")
            
            if not request:
                # If no request object was injected, we skip caching or 
                # we could hash args/kwargs. Let's hash kwargs for safety.
                # However, many times request isn't explicitly in kwargs unless added.
                pass
                
            # Create a cache key based on route, method, and query params
            # We also need to hash the request body for POSTs.
            key_parts = []
            
            if request:
                key_parts.append(request.method)
                key_parts.append(request.url.path)
                key_parts.append(str(request.query_params))
            else:
                key_parts.append(func.__name__)
                
            # To handle body safely in endpoints, we hash the stringified kwargs 
            # (excluding the Request and Response objects)
            clean_kwargs = {}
            for k, v in kwargs.items():
                if isinstance(v, (Request, Response)):
                    continue
                # For Pydantic models (like PredictionRequest), we can dump to dict
                if hasattr(v, "model_dump"):
                    clean_kwargs[k] = v.model_dump()
                else:
                    clean_kwargs[k] = str(v)
                    
            if clean_kwargs:
                key_parts.append(json.dumps(clean_kwargs, sort_keys=True))
                
            cache_key = "cache:" + hashlib.md5("|".join(key_parts).encode()).hexdigest()
            
            # Check cache
            cached_result = CacheService.get(cache_key)
            if cached_result is not None:
                CacheService.increment_hit()
                # Return standard dict/list which FastAPI will serialize correctly
                # Or return a JSONResponse
                return cached_result
                
            # Cache miss
            CacheService.increment_miss()
            
            # Execute original function (could be async or sync)
            import inspect
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            # Serialize result for caching
            cacheable_result = result
            if hasattr(result, "model_dump"):
                cacheable_result = result.model_dump()
            elif isinstance(result, Response):
                # Cannot easily cache FastAPI Response objects directly without extracting body
                cacheable_result = None
                
            if cacheable_result is not None:
                CacheService.set(cache_key, cacheable_result, ttl=ttl)
                
            return result
            
        return wrapper
    return decorator
