"""
Tests for LanguageToolProcessor.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.language_analysis.processors.language_tool_processor import LanguageToolProcessor


class TestLanguageToolProcessor:
    """Test cases for LanguageToolProcessor."""
    
    def test_language_tool_processor_initialization(self):
        """Test LanguageToolProcessor initialization."""
        processor = LanguageToolProcessor(language="de")
        
        assert processor.language == "de"
        assert processor.tool is None
        assert processor._is_loaded is False
    
    def test_language_tool_processor_defaults(self):
        """Test LanguageToolProcessor with default values."""
        processor = LanguageToolProcessor()
        
        assert processor.language == "de"
        assert processor.tool is None
        assert processor._is_loaded is False
    
    def test_is_loaded_false_when_not_loaded(self):
        """Test is_loaded returns False when tool not loaded."""
        processor = LanguageToolProcessor()
        
        assert processor.is_loaded() is False
    
    def test_is_loaded_true_when_loaded(self):
        """Test is_loaded returns True when tool is loaded."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        assert processor.is_loaded() is True
    
    def test_is_loaded_false_when_tool_is_none(self):
        """Test is_loaded returns False when tool is None."""
        processor = LanguageToolProcessor()
        processor._is_loaded = True
        processor.tool = None
        
        assert processor.is_loaded() is False
    
    @patch('src.services.language_analysis.processors.language_tool_processor.language_tool_python.LanguageTool')
    def test_load_model_success(self, mock_language_tool):
        """Test successful model loading."""
        processor = LanguageToolProcessor(language="de")
        mock_tool_instance = Mock()
        mock_language_tool.return_value = mock_tool_instance
        
        processor.load_model()
        
        mock_language_tool.assert_called_once_with("de")
        assert processor.tool == mock_tool_instance
        assert processor._is_loaded is True
    
    @patch('src.services.language_analysis.processors.language_tool_processor.language_tool_python.LanguageTool')
    def test_load_model_failure(self, mock_language_tool):
        """Test model loading failure."""
        processor = LanguageToolProcessor(language="de")
        mock_language_tool.side_effect = Exception("LanguageTool loading failed")
        
        with pytest.raises(Exception, match="Could not initialize LanguageTool for de: LanguageTool loading failed"):
            processor.load_model()
    
    def test_check_text_not_loaded(self):
        """Test check_text raises exception when tool not loaded."""
        processor = LanguageToolProcessor()
        
        with pytest.raises(Exception, match="LanguageTool not loaded. Call load_model\\(\\) first."):
            processor.check_text("Test text")
    
    def test_check_text_empty_text(self):
        """Test check_text with empty text."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        result = processor.check_text("")
        
        assert result == []
    
    def test_check_text_whitespace_text(self):
        """Test check_text with whitespace-only text."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        result = processor.check_text("   \n\t   ")
        
        assert result == []
    
    @patch('src.services.language_analysis.processors.language_tool_processor.time.time')
    def test_check_text_success(self, mock_time):
        """Test successful text checking."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        # Mock time.time to return consistent values
        mock_time.side_effect = [0.0, 0.1]  # start_time, end_time
        
        # Mock LanguageTool match
        mock_match = Mock()
        mock_match.message = "Possible spelling mistake found."
        mock_match.offset = 0
        mock_match.errorLength = 4
        mock_match.replacements = ["Hello", "Hallo"]
        mock_match.ruleId = "GERMAN_SPELLER_RULE"
        
        processor.tool.check.return_value = [mock_match]
        
        result = processor.check_text("Hllo World")
        
        assert len(result) == 1
        assert result[0].message == "Possible spelling mistake found."
        assert result[0].startChar == 0
        assert result[0].endChar == 4
        assert result[0].suggestions == ["Hello", "Hallo"]
        assert result[0].ruleId == "GERMAN_SPELLER_RULE"
    
    def test_check_grammar_only_not_loaded(self):
        """Test check_grammar_only raises exception when tool not loaded."""
        processor = LanguageToolProcessor()
        
        with pytest.raises(Exception, match="LanguageTool not loaded. Call load_model\\(\\) first."):
            processor.check_grammar_only("Test text")
    
    def test_check_grammar_only_empty_text(self):
        """Test check_grammar_only with empty text."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        result = processor.check_grammar_only("")
        
        assert result == []
    
    def test_check_grammar_only_filters_spelling_errors(self):
        """Test check_grammar_only filters out spelling errors."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        # Mock check_text to return mixed errors
        mock_grammar_error = Mock()
        mock_grammar_error.ruleId = "GERMAN_CASE_AGREEMENT"
        mock_grammar_error.message = "Grammar error"
        mock_grammar_error.offset = 0
        mock_grammar_error.errorLength = 5
        mock_grammar_error.replacements = ["correct"]
        
        mock_spelling_error = Mock()
        mock_spelling_error.ruleId = "GERMAN_SPELLER_RULE"
        mock_spelling_error.message = "Spelling error"
        mock_spelling_error.offset = 10
        mock_spelling_error.errorLength = 3
        mock_spelling_error.replacements = ["spell"]
        
        processor.tool.check.return_value = [mock_grammar_error, mock_spelling_error]
        
        result = processor.check_grammar_only("Test text")
        
        assert len(result) == 1
        assert result[0].ruleId == "GERMAN_CASE_AGREEMENT"
    
    def test_check_spelling_only_not_loaded(self):
        """Test check_spelling_only raises exception when tool not loaded."""
        processor = LanguageToolProcessor()
        
        with pytest.raises(Exception, match="LanguageTool not loaded. Call load_model\\(\\) first."):
            processor.check_spelling_only("Test text")
    
    def test_check_spelling_only_empty_text(self):
        """Test check_spelling_only with empty text."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        result = processor.check_spelling_only("")
        
        assert result == []
    
    def test_check_spelling_only_filters_grammar_errors(self):
        """Test check_spelling_only filters out grammar errors."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        # Mock check_text to return mixed errors
        mock_grammar_error = Mock()
        mock_grammar_error.ruleId = "GERMAN_CASE_AGREEMENT"
        mock_grammar_error.message = "Grammar error"
        mock_grammar_error.offset = 0
        mock_grammar_error.errorLength = 5
        mock_grammar_error.replacements = ["correct"]
        
        mock_spelling_error = Mock()
        mock_spelling_error.ruleId = "GERMAN_SPELLER_RULE"
        mock_spelling_error.message = "Spelling error"
        mock_spelling_error.offset = 5
        mock_spelling_error.errorLength = 3
        mock_spelling_error.replacements = ["spell"]
        
        processor.tool.check.return_value = [mock_grammar_error, mock_spelling_error]
        
        result = processor.check_spelling_only("Test text")
        
        assert len(result) == 1
        assert result[0].ruleId == "GERMAN_SPELLER_RULE"
    
    def test_get_supported_languages(self):
        """Test get_supported_languages returns list of languages."""
        processor = LanguageToolProcessor()
        
        languages = processor.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "de" in languages
        assert "en" in languages
        assert "fr" in languages
        assert "es" in languages
    
    def test_is_language_supported_true(self):
        """Test is_language_supported returns True for supported languages."""
        processor = LanguageToolProcessor()
        
        assert processor.is_language_supported("de") is True
        assert processor.is_language_supported("en") is True
        assert processor.is_language_supported("fr") is True
    
    def test_is_language_supported_false(self):
        """Test is_language_supported returns False for unsupported languages."""
        processor = LanguageToolProcessor()
        
        assert processor.is_language_supported("xyz") is False
        assert processor.is_language_supported("invalid") is False
    
    def test_get_rule_categories_not_loaded(self):
        """Test get_rule_categories returns empty dict when not loaded."""
        processor = LanguageToolProcessor()
        
        result = processor.get_rule_categories()
        
        assert result == {}
    
    def test_get_rule_categories_loaded(self):
        """Test get_rule_categories returns categories when loaded."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        result = processor.get_rule_categories()
        
        assert isinstance(result, dict)
        assert "grammar" in result
        assert "spelling" in result
        assert "style" in result
    
    def test_unload_model(self):
        """Test model unloading."""
        processor = LanguageToolProcessor()
        processor.tool = Mock()
        processor._is_loaded = True
        
        processor.unload_model()
        
        assert processor.tool is None
        assert processor._is_loaded is False
    
    def test_unload_model_when_tool_is_none(self):
        """Test model unloading when tool is already None."""
        processor = LanguageToolProcessor()
        processor.tool = None
        processor._is_loaded = False
        
        processor.unload_model()
        
        assert processor.tool is None
        assert processor._is_loaded is False
