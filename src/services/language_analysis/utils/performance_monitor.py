"""
Performance monitoring utilities for the language analysis service.

This module provides performance tracking, metrics collection, and monitoring
capabilities to help optimize the language analysis pipeline.
"""

import time
from typing import Dict, Any, List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from dataclasses import dataclass, field
from collections import defaultdict, deque
from src.services.logging.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    request_count: int = 0
    total_processing_time_ms: float = 0.0
    average_processing_time_ms: float = 0.0
    min_processing_time_ms: float = float('inf')
    max_processing_time_ms: float = 0.0
    error_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_updated: float = field(default_factory=time.time)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    start_time: float
    end_time: Optional[float] = None
    processing_time_ms: Optional[float] = None
    text_length: int = 0
    word_count: int = 0
    success: bool = True
    error_message: Optional[str] = None
    cache_hit: bool = False


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection for the language analysis service.
    
    This class tracks various performance metrics including processing times,
    error rates, cache performance, and system resource usage.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            max_history (int): Maximum number of request metrics to keep in history
        """
        self.max_history = max_history
        self.metrics = PerformanceMetrics()
        self.request_history: deque = deque(maxlen=max_history)
        self.component_times: Dict[str, List[float]] = defaultdict(list)
        self.start_time = time.time()
        logger.info("Performance monitor initialized")
    
    def start_request(self, text: str) -> RequestMetrics:
        """
        Start tracking a new request.
        
        Args:
            text (str): The text being analyzed
            
        Returns:
            RequestMetrics: The request metrics object to track
        """
        return RequestMetrics(
            start_time=time.time(),
            text_length=len(text),
            word_count=len(text.split())
        )
    
    def end_request(self, request_metrics: RequestMetrics, success: bool = True, 
                   error_message: Optional[str] = None, cache_hit: bool = False) -> None:
        """
        End tracking a request and update metrics.
        
        Args:
            request_metrics (RequestMetrics): The request metrics to finalize
            success (bool): Whether the request was successful
            error_message (Optional[str]): Error message if request failed
            cache_hit (bool): Whether the result came from cache
        """
        current_time = time.time()
        request_metrics.end_time = current_time
        request_metrics.processing_time_ms = (current_time - request_metrics.start_time) * 1000
        request_metrics.success = success
        request_metrics.error_message = error_message
        request_metrics.cache_hit = cache_hit
        
        # Update metrics
        self.metrics.request_count += 1
        self.metrics.last_updated = current_time
        
        if success:
            processing_time = request_metrics.processing_time_ms
            self.metrics.total_processing_time_ms += processing_time
            self.metrics.average_processing_time_ms = (
                self.metrics.total_processing_time_ms / self.metrics.request_count
            )
            self.metrics.min_processing_time_ms = min(
                self.metrics.min_processing_time_ms, processing_time
            )
            self.metrics.max_processing_time_ms = max(
                self.metrics.max_processing_time_ms, processing_time
            )
        else:
            self.metrics.error_count += 1
        
        if cache_hit:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
        
        # Add to history
        self.request_history.append(request_metrics)
        
        logger.debug(f"Request completed: {processing_time:.2f}ms, success={success}, cache_hit={cache_hit}")
    
    def track_component_time(self, component: str, duration_ms: float) -> None:
        """
        Track processing time for a specific component.
        
        Args:
            component (str): Name of the component (e.g., 'spacy', 'stanza', 'spellcheck')
            duration_ms (float): Processing time in milliseconds
        """
        self.component_times[component].append(duration_ms)
        
        # Keep only recent measurements (last 100 per component)
        if len(self.component_times[component]) > 100:
            self.component_times[component] = self.component_times[component][-100:]
    
    def __get_system_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage.
        
        Returns:
            Dict[str, Any]: System resource information
        """
        if not PSUTIL_AVAILABLE:
            return {
                "error": "psutil not available",
                "uptime_seconds": time.time() - self.start_time
            }
        
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            return {
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory.percent
                },
                "cpu": {
                    "percent_used": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "uptime_seconds": time.time() - self.start_time
            }
        except Exception as e:
            logger.warning(f"Failed to get system resources: {e}")
            return {"error": str(e)}
    
    def __get_component_stats(self) -> Dict[str, Any]:
        """
        Get statistics for each processing component.
        
        Returns:
            Dict[str, Any]: Component performance statistics
        """
        stats = {}
        
        for component, times in self.component_times.items():
            if times:
                stats[component] = {
                    "count": len(times),
                    "avg_time_ms": round(sum(times) / len(times), 2),
                    "min_time_ms": round(min(times), 2),
                    "max_time_ms": round(max(times), 2),
                    "total_time_ms": round(sum(times), 2)
                }
            else:
                stats[component] = {
                    "count": 0,
                    "avg_time_ms": 0,
                    "min_time_ms": 0,
                    "max_time_ms": 0,
                    "total_time_ms": 0
                }
        
        return stats
    
    def __get_recent_requests(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent request metrics.
        
        Args:
            count (int): Number of recent requests to return
            
        Returns:
            List[Dict[str, Any]]: Recent request information
        """
        recent = list(self.request_history)[-count:]
        
        return [
            {
                "processing_time_ms": req.processing_time_ms,
                "text_length": req.text_length,
                "word_count": req.word_count,
                "success": req.success,
                "cache_hit": req.cache_hit,
                "error_message": req.error_message
            }
            for req in recent
        ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive performance summary.
        
        Returns:
            Dict[str, Any]: Complete performance metrics and statistics
        """
        total_requests = self.metrics.request_count
        success_rate = ((total_requests - self.metrics.error_count) / total_requests * 100) if total_requests > 0 else 0
        
        cache_total = self.metrics.cache_hits + self.metrics.cache_misses
        cache_hit_rate = (self.metrics.cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            "overview": {
                "total_requests": total_requests,
                "success_rate_percent": round(success_rate, 2),
                "error_count": self.metrics.error_count,
                "uptime_seconds": time.time() - self.start_time
            },
            "performance": {
                "avg_processing_time_ms": round(self.metrics.average_processing_time_ms, 2),
                "min_processing_time_ms": round(self.metrics.min_processing_time_ms, 2) if self.metrics.min_processing_time_ms != float('inf') else 0,
                "max_processing_time_ms": round(self.metrics.max_processing_time_ms, 2),
                "total_processing_time_ms": round(self.metrics.total_processing_time_ms, 2)
            },
            "cache": {
                "hits": self.metrics.cache_hits,
                "misses": self.metrics.cache_misses,
                "hit_rate_percent": round(cache_hit_rate, 2)
            },
            "components": self.__get_component_stats(),
            "system": self.__get_system_resources(),
            "recent_requests": self.__get_recent_requests(5)
        }
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.metrics = PerformanceMetrics()
        self.request_history.clear()
        self.component_times.clear()
        self.start_time = time.time()
        logger.info("Performance metrics reset")


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance.
    
    Returns:
        PerformanceMonitor: The global performance monitor
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def reset_performance_metrics() -> None:
    """Reset the global performance metrics."""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.reset_metrics()
