"""
Model Management Utilities

This module provides utilities for managing NLP models including loading,
initialization, and PyTorch compatibility fixes.
"""

import torch
from torch.serialization import add_safe_globals
from typing import Optional, Dict, Any
from ...logging.logging import get_logger

logger = get_logger(__name__)


class ModelManager:
    """Model management utilities for NLP processors."""
    
    def __init__(self):
        """Initialize the model manager."""
        self._torch_patched = False
        self._apply_torch_patches()
    
    def _apply_torch_patches(self) -> None:
        """
        Apply PyTorch compatibility patches for Stanza.
        
        This method handles compatibility issues between Stanza and newer PyTorch versions.
        """
        if self._torch_patched:
            return
        
        try:
            # PyTorch/Stanza Compatibility Fix
            from numpy.core.multiarray import _reconstruct
            add_safe_globals([_reconstruct])
            
            # Monkey-patch torch.load to default to weights_only=False for Stanza compatibility
            self._original_torch_load = torch.load
            
            def patched_torch_load(*args, **kwargs):
                """
                Patched version of torch.load to ensure Stanza compatibility.
                
                Stanza models require weights_only=False to load properly, but newer PyTorch
                versions default to weights_only=True for security. This patch ensures
                compatibility while maintaining the original functionality.
                """
                if "weights_only" not in kwargs:
                    kwargs["weights_only"] = False
                return self._original_torch_load(*args, **kwargs)
            
            torch.load = patched_torch_load
            self._torch_patched = True
            logger.info("PyTorch compatibility patches applied successfully")
            
        except Exception as e:
            logger.warning(f"Failed to apply PyTorch patches: {e}")
    
    def get_model_info(self, processor_name: str, model_loaded: bool) -> Dict[str, Any]:
        """
        Get information about a model's loading status.
        
        Args:
            processor_name (str): Name of the processor
            model_loaded (bool): Whether the model is loaded
            
        Returns:
            Dict[str, Any]: Model information
        """
        return {
            "processor": processor_name,
            "loaded": model_loaded,
            "torch_patched": self._torch_patched
        }
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resources for model loading.
        
        Returns:
            Dict[str, Any]: System resource information
        """
        try:
            import psutil
            
            # Get memory information
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent
            }
            
            # Get CPU information
            cpu_info = {
                "count": psutil.cpu_count(),
                "usage_percent": psutil.cpu_percent(interval=1)
            }
            
            return {
                "memory": memory_info,
                "cpu": cpu_info,
                "torch_patched": self._torch_patched
            }
            
        except ImportError:
            logger.warning("psutil not available, cannot check system resources")
            return {
                "memory": {"error": "psutil not available"},
                "cpu": {"error": "psutil not available"},
                "torch_patched": self._torch_patched
            }
        except Exception as e:
            logger.error(f"Failed to check system resources: {e}")
            return {
                "memory": {"error": str(e)},
                "cpu": {"error": str(e)},
                "torch_patched": self._torch_patched
            }
    
    def validate_model_requirements(self, processor_name: str) -> Dict[str, Any]:
        """
        Validate that system meets requirements for a specific processor.
        
        Args:
            processor_name (str): Name of the processor to validate
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation = {
            "processor": processor_name,
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check system resources
        resources = self.check_system_resources()
        
        # Memory check
        if "memory" in resources and "available_gb" in resources["memory"]:
            available_memory = resources["memory"]["available_gb"]
            if available_memory < 2.0:
                validation["warnings"].append(f"Low available memory: {available_memory}GB")
            if available_memory < 1.0:
                validation["valid"] = False
                validation["errors"].append(f"Insufficient memory: {available_memory}GB")
        
        # CPU check
        if "cpu" in resources and "count" in resources["cpu"]:
            cpu_count = resources["cpu"]["count"]
            if cpu_count < 2:
                validation["warnings"].append(f"Low CPU count: {cpu_count}")
        
        # PyTorch compatibility
        if not self._torch_patched:
            validation["warnings"].append("PyTorch compatibility patches not applied")
        
        logger.debug(f"Model requirements validation for {processor_name}: {validation}")
        return validation
    
    def cleanup_resources(self) -> None:
        """Clean up resources and restore original torch.load if needed."""
        if self._torch_patched and hasattr(self, '_original_torch_load'):
            torch.load = self._original_torch_load
            self._torch_patched = False
            logger.info("PyTorch patches restored")
    
    def __del__(self):
        """Cleanup when the model manager is destroyed."""
        self.cleanup_resources()
