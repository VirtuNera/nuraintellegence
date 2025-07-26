"""
Performance caching utilities to reduce database queries and API calls
"""

import json
import time
from functools import wraps
from typing import Any, Dict, Optional

class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expires']:
                return entry['value']
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:  # 5 min default
        """Set value in cache with TTL in seconds"""
        self._cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()

# Global cache instance
cache = SimpleCache()

def cached(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

def cache_key(prefix: str, *args) -> str:
    """Generate cache key from prefix and arguments"""
    return f"{prefix}:{hash(str(args))}"