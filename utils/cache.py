import json
import time
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime
import config
from utils.logger import cache_logger

class Cache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self._content_types = {}
        cache_logger.info("Cache initialized")

    def _generate_key(self, data: str) -> str:
        """Generate a unique key for the cache entry."""
        key = hashlib.md5(data.encode()).hexdigest()
        cache_logger.debug(f"Generated cache key: {key} for data: {data[:50]}...")
        return key

    def _get_expiration_time(self, content_type: str) -> int:
        """Get the expiration time in seconds for a given content type."""
        expiration = config.CACHE_EXPIRATION.get(content_type, config.CACHE_EXPIRATION['historical'])
        cache_logger.debug(f"Expiration time for {content_type}: {expiration} seconds")
        return expiration

    def set(self, data: str, value: Any, content_type: str = 'historical') -> str:
        """
        Store a value in the cache.
        
        Args:
            data: The data to generate the key from
            value: The value to store
            content_type: Type of content ('news', 'academic', or 'historical')
            
        Returns:
            The cache key
        """
        key = self._generate_key(data)
        self._cache[key] = value
        self._timestamps[key] = time.time()
        self._content_types[key] = content_type
        cache_logger.info(f"Cached item with key {key}, content type: {content_type}")
        return key

    def get(self, data: str) -> Optional[Any]:
        """
        Retrieve a value from the cache if it exists and hasn't expired.
        
        Args:
            data: The data to generate the key from
            
        Returns:
            The cached value or None if not found or expired
        """
        key = self._generate_key(data)
        if key not in self._cache:
            cache_logger.debug(f"Cache miss for key: {key}")
            return None

        # Check if the entry has expired
        current_time = time.time()
        stored_time = self._timestamps[key]
        content_type = self._content_types[key]
        expiration_time = self._get_expiration_time(content_type)

        if current_time - stored_time > expiration_time:
            # Remove expired entry
            cache_logger.info(f"Cache entry expired for key: {key}, content type: {content_type}")
            self.invalidate(data)
            return None

        cache_logger.info(f"Cache hit for key: {key}, content type: {content_type}")
        return self._cache[key]

    def invalidate(self, data: str) -> None:
        """
        Remove an entry from the cache.
        
        Args:
            data: The data to generate the key from
        """
        key = self._generate_key(data)
        if key in self._cache:
            content_type = self._content_types.get(key, "unknown")
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self._content_types.pop(key, None)
            cache_logger.info(f"Invalidated cache entry with key: {key}, content type: {content_type}")
        else:
            cache_logger.debug(f"Attempted to invalidate non-existent cache key: {key}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        cache_size = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        self._content_types.clear()
        cache_logger.info(f"Cleared entire cache with {cache_size} entries")

class SearchCache(Cache):
    """Specialized cache for search results."""
    
    def set_search_results(self, query: str, results: list) -> str:
        """
        Cache search results with metadata.
        
        Args:
            query: The search query
            results: List of search results
            
        Returns:
            Cache key
        """
        cache_logger.info(f"Caching search results for query: {query}")
        cache_logger.debug(f"Caching {len(results)} search results")
        cache_data = {
            'query': query,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        return self.set(query, cache_data, 'news')

class ReportCache(Cache):
    """Specialized cache for generated reports."""
    
    def set_report(self, query: str, report: Dict[str, Any], content_type: str = 'academic') -> str:
        """
        Cache a generated report.
        
        Args:
            query: The research query
            report: The generated report
            content_type: Type of content
            
        Returns:
            Cache key
        """
        cache_logger.info(f"Caching report for query: {query}")
        cache_logger.debug(f"Report content type: {content_type}")
        cache_data = {
            'query': query,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }
        return self.set(query, cache_data, content_type)

# Global cache instances
search_cache = SearchCache()
report_cache = ReportCache() 