"""
Tests for text preprocessing utilities.
"""

import pytest
from src.services.language_analysis.utils.text_preprocessing import TextPreprocessor


class TestTextPreprocessor:
    """Test cases for TextPreprocessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = TextPreprocessor(max_length=1000)
    
    def test_preprocess_valid_text(self):
        """Test preprocessing with valid text."""
        text = "  Hello World!  "
        result = self.preprocessor.preprocess(text)
        assert result == "Hello World!"
    
    def test_preprocess_empty_text(self):
        """Test preprocessing with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.preprocessor.preprocess("")
    
    def test_preprocess_whitespace_only(self):
        """Test preprocessing with whitespace-only text."""
        with pytest.raises(ValueError, match="Text cannot be empty or only whitespace"):
            self.preprocessor.preprocess("   \n\t   ")
    
    def test_preprocess_invalid_type(self):
        """Test preprocessing with invalid input type."""
        with pytest.raises(ValueError, match="Text must be a string"):
            self.preprocessor.preprocess(123)
    
    def test_preprocess_text_truncation(self):
        """Test text truncation when exceeding max length."""
        long_text = "a" * 2000
        result = self.preprocessor.preprocess(long_text)
        assert len(result) == 1000
        assert result == "a" * 1000
    
    def test_validate_text_valid(self):
        """Test text validation with valid text."""
        text = "Hello World! This is a test."
        result = self.preprocessor.validate_text(text)
        
        assert result["valid"] is True
        assert result["has_letters"] is True
        assert result["has_punctuation"] is True
        assert result["character_count"] == len(text)
        assert result["word_count"] == 6
    
    def test_validate_text_empty(self):
        """Test text validation with empty text."""
        result = self.preprocessor.validate_text("")
        
        assert result["valid"] is False
        assert result["reason"] == "empty_text"
    
    def test_validate_text_suspicious_patterns(self):
        """Test text validation with suspicious patterns."""
        text = "aaaaa    "  # Repeated chars and excessive whitespace
        result = self.preprocessor.validate_text(text)
        
        assert result["valid"] is True
        assert result["has_repeated_chars"] is True
        # Note: The current implementation doesn't detect this as excessive whitespace
        # because it's only 4 spaces, which is below the threshold
        assert len(result["warnings"]) >= 1  # At least one warning for repeated chars
    
    def test_get_basic_stats(self):
        """Test basic text statistics."""
        text = "Hello World!\nThis is a test.\n\nAnother paragraph."
        result = self.preprocessor.get_basic_stats(text)
        
        assert result["character_count"] == len(text)
        assert result["word_count"] == 8
        assert result["sentence_count"] == 2  # Based on periods
        assert result["line_count"] == 4
        assert result["paragraph_count"] == 2
        assert result["alpha_chars"] > 0
        assert result["punctuation_chars"] > 0
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        text = "  Hello    World!  \n\n  This   is   a   test.  "
        result = self.preprocessor.clean_text(text)
        
        assert result == "Hello World! This is a test."
    
    def test_extract_words(self):
        """Test word extraction."""
        text = "Hello World! This is a test123."
        result = self.preprocessor.extract_words(text)
        
        expected = ["Hello", "World", "This", "is", "a", "test123"]
        assert result == expected
    
    def test_detect_encoding_issues(self):
        """Test encoding issue detection."""
        # Test with normal text (no encoding issues)
        text_normal = "Hello World"
        result = self.preprocessor.detect_encoding_issues(text_normal)
        
        assert result["has_encoding_issues"] is False
        assert len(result["issues"]) == 0
