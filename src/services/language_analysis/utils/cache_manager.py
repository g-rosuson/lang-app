"""
Cache management utilities for the language analysis service.

This module provides caching functionality to improve performance by avoiding
redundant processing of identical text inputs.
"""

import hashlib
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from src.services.logging.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """Represents a cached analysis result."""
    result: Dict[str, Any]
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0.0


class AnalysisCache:
    """
    Simple in-memory cache for language analysis results.
    
    This cache stores analysis results to avoid reprocessing identical text inputs.
    It includes TTL (time-to-live) functionality and access tracking for cache
    management and performance monitoring.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the analysis cache.
        
        Args:
            max_size (int): Maximum number of entries to store
            ttl_seconds (int): Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
        logger.info(f"Analysis cache initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def _generate_key(self, text: str, language: str = "de") -> str:
        """
        Generate a cache key for the given text and language.
        
        Args:
            text (str): The text to analyze
            language (str): The language code
            
        Returns:
            str: A unique cache key
        """
        # Normalize text for consistent caching
        normalized_text = text.strip().lower()
        
        # Create hash of text + language
        content = f"{normalized_text}:{language}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get(self, text: str, language: str = "de") -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached analysis result.
        
        Args:
            text (str): The text that was analyzed
            language (str): The language code
            
        Returns:
            Optional[Dict[str, Any]]: Cached result if found and valid, None otherwise
        """
        key = self._generate_key(text, language)
        current_time = time.time()
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if entry has expired
            if current_time - entry.timestamp > self.ttl_seconds:
                del self.cache[key]
                self.misses += 1
                logger.debug(f"Cache miss (expired): {key[:8]}...")
                return None
            
            # Update access statistics
            entry.access_count += 1
            entry.last_accessed = current_time
            self.hits += 1
            logger.debug(f"Cache hit: {key[:8]}... (access #{entry.access_count})")
            return entry.result
        
        self.misses += 1
        logger.debug(f"Cache miss (not found): {key[:8]}...")
        return None
    
    def set(self, text: str, result: Dict[str, Any], language: str = "de") -> None:
        """
        Store an analysis result in the cache.
        
        Args:
            text (str): The text that was analyzed
            result (Dict[str, Any]): The analysis result
            language (str): The language code
        """
        key = self._generate_key(text, language)
        current_time = time.time()
        
        # Check if we need to evict entries
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        # Store the result
        self.cache[key] = CacheEntry(
            result=result,
            timestamp=current_time,
            access_count=1,
            last_accessed=current_time
        )
        
        logger.debug(f"Cache set: {key[:8]}... (size: {len(self.cache)})")
    
    def _evict_oldest(self) -> None:
        """Evict the least recently accessed entry."""
        if not self.cache:
            return
        
        # Find the entry with the oldest last_accessed time
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        del self.cache[oldest_key]
        logger.debug(f"Cache evicted: {oldest_key[:8]}... (size: {len(self.cache)})")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        size = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache cleared: {size} entries removed")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics including hit rate, size, etc.
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate average access count
        avg_access_count = 0
        if self.cache:
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            avg_access_count = total_accesses / len(self.cache)
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "ttl_seconds": self.ttl_seconds,
            "avg_access_count": round(avg_access_count, 2)
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from the cache.
        
        Returns:
            int: Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry.timestamp > self.ttl_seconds
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"Cache cleanup: {len(expired_keys)} expired entries removed")
        
        return len(expired_keys)


# Global cache instance
_cache_instance: Optional[AnalysisCache] = None


def get_analysis_cache() -> AnalysisCache:
    """
    Get the global analysis cache instance.
    
    Returns:
        AnalysisCache: The global cache instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AnalysisCache()
    return _cache_instance


def clear_analysis_cache() -> None:
    """Clear the global analysis cache."""
    global _cache_instance
    if _cache_instance:
        _cache_instance.clear()
