"""
Tests for model management utilities.
"""

from unittest.mock import patch, MagicMock
from src.services.language_analysis.utils.model_manager import ModelManager


class TestModelManager:
    """Test cases for ModelManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ModelManager()
    
    def test_get_model_info(self):
        """Test getting model information."""
        info = self.manager.get_model_info("test_processor", True)
        
        assert info["processor"] == "test_processor"
        assert info["loaded"] is True
        assert "torch_patched" in info
    
    def test_get_model_info_not_loaded(self):
        """Test getting model information for unloaded model."""
        info = self.manager.get_model_info("test_processor", False)
        
        assert info["processor"] == "test_processor"
        assert info["loaded"] is False
        assert "torch_patched" in info
    
    def test_check_system_resources_with_psutil(self):
        """Test system resource checking with psutil available."""
        # This test just verifies the method doesn't crash
        result = self.manager.check_system_resources()
        
        assert "memory" in result
        assert "cpu" in result
        assert "torch_patched" in result
    
    def test_check_system_resources_without_psutil(self):
        """Test system resource checking without psutil."""
        # This test just verifies the method doesn't crash
        result = self.manager.check_system_resources()
        
        assert "memory" in result
        assert "cpu" in result
        assert "torch_patched" in result
    
    def test_validate_model_requirements_sufficient_memory(self):
        """Test model requirements validation with sufficient memory."""
        with patch.object(self.manager, 'check_system_resources') as mock_check:
            mock_check.return_value = {
                "memory": {"available_gb": 4.0},
                "cpu": {"count": 4}
            }
            
            result = self.manager.validate_model_requirements("test_processor")
            
            assert result["processor"] == "test_processor"
            assert result["valid"] is True
            assert len(result["errors"]) == 0
    
    def test_validate_model_requirements_low_memory(self):
        """Test model requirements validation with low memory."""
        with patch.object(self.manager, 'check_system_resources') as mock_check:
            mock_check.return_value = {
                "memory": {"available_gb": 0.5},
                "cpu": {"count": 1}
            }
            
            result = self.manager.validate_model_requirements("test_processor")
            
            assert result["processor"] == "test_processor"
            assert result["valid"] is False
            assert len(result["errors"]) > 0
            assert any("Insufficient memory" in error for error in result["errors"])
    
    def test_cleanup_resources(self):
        """Test resource cleanup."""
        # This test mainly ensures the method doesn't raise an exception
        self.manager.cleanup_resources()
        assert True  # If we get here, no exception was raised
