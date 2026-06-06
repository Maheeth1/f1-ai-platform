from fastapi import APIRouter
from app.services.cache_service import CacheService

router = APIRouter()

@router.get("/cache/metrics")
def get_cache_metrics():
    """Returns hit/miss metrics for the Redis cache."""
    return CacheService.get_metrics()
