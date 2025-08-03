"""
BrainSAIT Healthcare Platform - Caching Module
Provides efficient caching mechanisms for the healthcare platform.

This module implements a flexible caching system that works with both
Redis (when available) and in-memory caching as a fallback.
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Union, List, TypeVar, Generic, Callable
from datetime import datetime, timedelta
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheManager:
    """
    Unified caching manager that supports both Redis and in-memory caching

    This class provides a consistent interface for caching data regardless
    of the underlying storage mechanism.
    """

    def __init__(
        self,
        redis_enabled: bool = False,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 3600  # 1 hour default
    ):
        """Initialize cache manager with appropriate backend"""
        self.redis_enabled = redis_enabled
        self.default_ttl = default_ttl
        self._redis_client = None

        # In-memory cache when Redis is not available
        self._memory_cache: Dict[str, Dict[str, Any]] = {}

        if redis_enabled:
            try:
                import redis.asyncio as redis
                self._redis_client = redis.from_url(redis_url)
                logger.info("Redis cache initialized")
            except ImportError:
                logger.warning("Redis package not installed, falling back to memory cache")
                self.redis_enabled = False
            except Exception as e:
                logger.error(f"Redis connection failed: {e}")
                self.redis_enabled = False

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache"""
        try:
            if self.redis_enabled and self._redis_client:
                value = await self._redis_client.get(key)
                if value:
                    return json.loads(value)
                return default
            else:
                # Memory cache with expiry check
                if key in self._memory_cache:
                    entry = self._memory_cache[key]
                    if entry["expires"] > time.time():
                        return entry["value"]
                    else:
                        # Expired, remove it
                        del self._memory_cache[key]
                return default

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set a value in cache with optional TTL"""
        ttl = ttl if ttl is not None else self.default_ttl

        try:
            serialized = json.dumps(value)

            if self.redis_enabled and self._redis_client:
                await self._redis_client.set(key, serialized, ex=ttl)
            else:
                # Store in memory with expiry time
                self._memory_cache[key] = {
                    "value": value,
                    "expires": time.time() + ttl
                }
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Remove a value from cache"""
        try:
            if self.redis_enabled and self._redis_client:
                await self._redis_client.delete(key)
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def flush(self) -> bool:
        """Clear all cached values"""
        try:
            if self.redis_enabled and self._redis_client:
                await self._redis_client.flushdb()
            else:
                self._memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {e}")
            return False

    async def keys_matching(self, pattern: str) -> List[str]:
        """Get keys matching pattern"""
        try:
            if self.redis_enabled and self._redis_client:
                return await self._redis_client.keys(pattern)
            else:
                # Simple pattern matching for memory cache
                import fnmatch
                return [k for k in self._memory_cache.keys()
                        if fnmatch.fnmatch(k, pattern)]
        except Exception as e:
            logger.error(f"Cache keys_matching error: {e}")
            return []

    def cached(
        self,
        prefix: str,
        ttl: Optional[int] = None,
        key_builder: Optional[Callable[..., str]] = None
    ):
        """
        Decorator for caching function results

        Args:
            prefix: Prefix for the cache key
            ttl: Time-to-live in seconds
            key_builder: Optional function to build cache key from args
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
                else:
                    # Default key from arguments
                    key_parts = [str(arg) for arg in args]
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = f"{prefix}:{':'.join(key_parts)}"

                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Call the function
                result = await func(*args, **kwargs)

                # Store in cache
                await self.set(cache_key, result, ttl)

                return result

            return wrapper

        return decorator

# Default cache instance
cache_manager = CacheManager()

# Initialize with Redis if available
def initialize_cache(redis_enabled=False, redis_url=None):
    """Initialize the cache with appropriate configuration"""
    global cache_manager
    cache_manager = CacheManager(
        redis_enabled=redis_enabled,
        redis_url=redis_url or "redis://localhost:6379/0"
    )
    return cache_manager
