import json
import time
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime
import config
from utils.logger import cache_logger
import streamlit as st

class Cache:
    def __init__(self, name="default"):
        self.name = name
        self._cache = {}
        self._timestamps = {}
        self._content_types = {}
        cache_logger.info(f"Cache '{name}' initialized with {len(self._cache)} items")

    def _generate_key(self, data: str) -> str:
        """Generate a unique key for the cache entry."""
        return hashlib.md5(data.encode()).hexdigest()

    def _get_expiration_time(self, content_type: str) -> int:
        """Get the expiration time in seconds for a given content type."""
        return config.CACHE_EXPIRATION.get(content_type, config.CACHE_EXPIRATION['historical'])

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
        cache_logger.debug(f"Cached item with key {key}, type: {content_type}, total items: {len(self._cache)}")
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
        
        if (current_time - stored_time) > expiration_time:
            # Remove expired entry
            cache_logger.debug(f"Cache entry expired for key: {key}")
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self._content_types.pop(key, None)
            return None

        cache_logger.debug(f"Cache hit for key: {key}")
        return self._cache[key]

    def invalidate(self, data: str) -> None:
        """
        Remove an entry from the cache.
        
        Args:
            data: The data to generate the key from
        """
        key = self._generate_key(data)
        if key in self._cache:
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            self._content_types.pop(key, None)
            cache_logger.debug(f"Invalidated cache entry with key: {key}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        item_count = len(self._cache)
        self._cache.clear()
        self._timestamps.clear()
        self._content_types.clear()
        cache_logger.info(f"Cache '{self.name}' cleared, removed {item_count} items")

class SearchCache(Cache):
    """Specialized cache for search results."""
    
    def __init__(self):
        super().__init__(name="search")
    
    def set_search_results(self, query: str, results: list) -> str:
        """
        Cache search results with metadata.
        
        Args:
            query: The search query
            results: List of search results
            
        Returns:
            Cache key
        """
        cache_data = {
            'query': query,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        return self.set(query, cache_data, 'news')

class ReportCache(Cache):
    """Specialized cache for generated reports."""
    
    def __init__(self):
        super().__init__(name="report")
    
    def get(self, data: str, ignore_short_content: bool = False) -> Optional[Any]:
        """
        Get a report from the cache
        
        Args:
            data: The query string
            ignore_short_content: If True, don't validate content length (useful for streaming)
            
        Returns:
            The cached report or None if not found
        """
        cached_data = super().get(data)
        if not cached_data:
            return None
            
        # Validate the report structure
        report = cached_data.get('report', {})
        
        # Check if report is empty
        if not report:
            self.invalidate(data)
            return None
            
        # Ensure content is a string
        if not isinstance(report['content'], str):
            report['content'] = str(report['content'])
            
        # Check if content is empty or too short
        if not ignore_short_content and (not report['content'] or len(report['content']) < 50):
            self.invalidate(data)
            return None
            
        return cached_data
    
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
        # Ensure the report is properly serializable
        try:
            json.dumps(report)
        except (TypeError, ValueError):
            # Create a clean copy with only serializable data
            clean_report = {
                "query": report.get("query", ""),
                "content": str(report.get("content", "")),
                "timestamp": report.get("timestamp", ""),
                "sources": []
            }
            
            # Process sources
            if "sources" in report and isinstance(report["sources"], list):
                for source in report["sources"]:
                    if isinstance(source, dict):
                        clean_report["sources"].append(source)
                    else:
                        try:
                            clean_report["sources"].append(dict(source))
                        except Exception:
                            clean_report["sources"].append({
                                "title": "Source",
                                "url": "",
                                "credibility": 0.3
                            })
            
            report = clean_report
        
        # Clean up any [object Object] artifacts in the content
        if "content" in report and isinstance(report["content"], str) and "[object Object]" in report["content"]:
            content = report["content"]
            
            # Remove standalone [object Object]
            content = content.replace("[object Object]", "")
            
            # Remove comma-separated [object Object] patterns
            content = content.replace(",[object Object],", ",")
            content = content.replace(",[object Object]", "")
            content = content.replace("[object Object],", "")
            
            # Remove repeated commas that might be left after cleaning
            while ",," in content:
                content = content.replace(",,", ",")
            
            # Remove leading/trailing commas in lines
            lines = content.split('\n')
            for i, line in enumerate(lines):
                lines[i] = line.strip(',')
            
            report["content"] = '\n'.join(lines)
        
        cache_data = {
            'query': query,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }
        return self.set(query, cache_data, content_type)

# Create cached instances of the caches
@st.cache_resource(ttl=None)
def get_search_cache(version=2):
    cache_logger.info(f"Creating persistent search cache (version {version})")
    return SearchCache()

@st.cache_resource(ttl=None)
def get_report_cache(version=2):
    cache_logger.info(f"Creating persistent report cache (version {version})")
    return ReportCache()

# Global cache instances - these will be shared across all sessions
search_cache = get_search_cache()
report_cache = get_report_cache() 