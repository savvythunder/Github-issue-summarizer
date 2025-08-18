"""
Caching service for improved performance and reduced API calls.
"""

import logging
import hashlib
import json
from typing import Any, Optional
from flask_caching import Cache

logger = logging.getLogger(__name__)

class CacheService:
    """Service for managing application caching."""
    
    def __init__(self, cache: Cache):
        self.cache = cache
        self.default_timeout = 1800  # 30 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        try:
            result = self.cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for key: {key}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            value: Data to cache
            timeout: Cache timeout in seconds
            
        Returns:
            Boolean indicating success
        """
        try:
            timeout = timeout or self.default_timeout
            self.cache.set(key, value, timeout=timeout)
            logger.debug(f"Cache set for key: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete data from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            Boolean indicating success
        """
        try:
            self.cache.delete(key)
            logger.debug(f"Cache deleted for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all cached data.
        
        Returns:
            Boolean indicating success
        """
        try:
            self.cache.clear()
            logger.info("All cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """
        Generate a consistent cache key from parameters.
        
        Args:
            prefix: Key prefix
            **kwargs: Key-value pairs to include in the key
            
        Returns:
            Generated cache key
        """
        # Sort kwargs for consistent key generation
        sorted_items = sorted(kwargs.items())
        key_string = f"{prefix}:{json.dumps(sorted_items, sort_keys=True)}"
        
        # Use hash for long keys to avoid key length issues
        if len(key_string) > 250:  # Most cache backends have key length limits
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        
        return key_string
    
    def get_or_set(self, key: str, callable_func, timeout: Optional[int] = None) -> Any:
        """
        Get data from cache or execute function and cache the result.
        
        Args:
            key: Cache key
            callable_func: Function to execute if cache miss
            timeout: Cache timeout in seconds
            
        Returns:
            Cached or computed data
        """
        try:
            # Try to get from cache first
            cached_value = self.get(key)
            if cached_value is not None:
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss for key: {key}, executing function")
            computed_value = callable_func()
            
            # Cache the result
            self.set(key, computed_value, timeout)
            
            return computed_value
            
        except Exception as e:
            logger.error(f"Error in get_or_set: {str(e)}")
            # Return computed value even if caching fails
            try:
                return callable_func()
            except Exception as compute_error:
                logger.error(f"Error executing function: {str(compute_error)}")
                raise compute_error
    
    def health_check(self) -> bool:
        """
        Check if caching service is working.
        
        Returns:
            Boolean indicating service health
        """
        try:
            test_key = "health_check_test"
            test_value = "test_value"
            
            # Test set and get
            self.set(test_key, test_value, timeout=60)
            retrieved_value = self.get(test_key)
            
            # Clean up
            self.delete(test_key)
            
            return retrieved_value == test_value
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get cache statistics if available.
        
        Returns:
            Cache statistics dictionary
        """
        try:
            # This will depend on the cache backend being used
            # For simple cache, we might not have detailed stats
            return {
                "status": "active",
                "default_timeout": self.default_timeout,
                "backend": str(type(self.cache.cache).__name__)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {"status": "unknown", "error": str(e)}
