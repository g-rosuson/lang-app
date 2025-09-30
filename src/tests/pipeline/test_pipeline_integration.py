"""
Tests for pipeline integration.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.language_analysis.pipeline import LanguageAnalysisPipeline
from src.services.language_analysis.models.analysis_result import AnalysisRequest


class TestLanguageAnalysisPipeline:
    """Test cases for LanguageAnalysisPipeline."""
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        config = {
            'stanza_language': 'de',
            'language_tool_language': 'de',
            'stanza_processors': 'tokenize,mwt,pos,lemma,depparse',
            'use_gpu': False
        }
        
        pipeline = LanguageAnalysisPipeline(config)
        
        assert pipeline.config == config
        assert pipeline._stanza_processors == {}
        assert pipeline._language_tool_processors == {}
        assert pipeline._is_initialized is False
        assert pipeline._initialization_errors == []
    
    def test_pipeline_initialization_defaults(self):
        """Test pipeline initialization with default config."""
        pipeline = LanguageAnalysisPipeline()
        
        assert pipeline.config == {}
        assert pipeline._stanza_processors == {}
        assert pipeline._language_tool_processors == {}
        assert pipeline._is_initialized is False
        assert pipeline._initialization_errors == []
    
    def test_is_initialized_false_when_not_initialized(self):
        """Test is_initialized returns False when not initialized."""
        pipeline = LanguageAnalysisPipeline()
        
        assert pipeline.is_initialized() is False
    
    def test_is_initialized_true_when_initialized(self):
        """Test is_initialized returns True when initialized."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        assert pipeline.is_initialized() is True
    
    def test_initialize_success(self):
        """Test successful pipeline initialization."""
        pipeline = LanguageAnalysisPipeline()
        
        pipeline.initialize()
        
        assert pipeline._is_initialized is True
        assert len(pipeline._initialization_errors) == 0
    
    def test_analyze_not_initialized(self):
        """Test analyze raises exception when pipeline not initialized."""
        pipeline = LanguageAnalysisPipeline()
        request = AnalysisRequest(text="Test text", language="de")
        
        with pytest.raises(Exception, match="Pipeline not initialized. Call initialize\\(\\) first."):
            pipeline.analyze(request)
    
    @patch.object(LanguageAnalysisPipeline, 'is_initialized')
    def test_analyze_success(self, mock_is_initialized):
        """Test successful analysis."""
        pipeline = LanguageAnalysisPipeline()
        mock_is_initialized.return_value = True
        
        # Mock the dynamic processor creation methods
        mock_stanza_processor = Mock()
        mock_language_tool_processor = Mock()
        mock_stanza_processor.analyze_comprehensive.return_value = []
        mock_language_tool_processor.check_text.return_value = []
        
        with patch.object(pipeline, '_LanguageAnalysisPipeline__get_stanza_processor', return_value=mock_stanza_processor):
            with patch.object(pipeline, '_LanguageAnalysisPipeline__get_language_tool_processor', return_value=mock_language_tool_processor):
                request = AnalysisRequest(
                    text="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
                    language="de",
                    include_grammar_check=True,
                    include_morphological_analysis=True,
                    include_dependency_parsing=True
                )
                
                result = pipeline.analyze(request)
                
                assert result.originalText == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
                assert result.language == "de"
                assert result.sentences == []
                assert result.errors == []
    
    def test_get_stanza_language_code_conversion(self):
        """Test language code conversion for Stanza."""
        pipeline = LanguageAnalysisPipeline()
        
        # Test short code remains unchanged
        assert pipeline._LanguageAnalysisPipeline__get_stanza_language_code("de") == "de"
        assert pipeline._LanguageAnalysisPipeline__get_stanza_language_code("en") == "en"
        
        # Test full code conversion to short
        assert pipeline._LanguageAnalysisPipeline__get_stanza_language_code("de-DE") == "de"
        assert pipeline._LanguageAnalysisPipeline__get_stanza_language_code("en-US") == "en"
        assert pipeline._LanguageAnalysisPipeline__get_stanza_language_code("fr-FR") == "fr"
    
    @patch('src.services.language_analysis.processors.stanza_processor.StanzaProcessor')
    def test_get_stanza_processor_caching(self, mock_stanza_class):
        """Test that Stanza processors are cached correctly."""
        pipeline = LanguageAnalysisPipeline()
        mock_processor = Mock()
        mock_processor.is_loaded.return_value = True
        mock_stanza_class.return_value = mock_processor
        
        # First call should create new processor
        processor1 = pipeline._LanguageAnalysisPipeline__get_stanza_processor("de")
        
        # Second call should return cached processor
        processor2 = pipeline._LanguageAnalysisPipeline__get_stanza_processor("de")
        
        assert processor1 is processor2
        assert "de" in pipeline._stanza_processors
        mock_stanza_class.assert_called_once()
    
    @patch('src.services.language_analysis.processors.language_tool_processor.LanguageToolProcessor')
    def test_get_language_tool_processor_caching(self, mock_lt_class):
        """Test that LanguageTool processors are cached correctly."""
        pipeline = LanguageAnalysisPipeline()
        mock_processor = Mock()
        mock_processor.is_loaded.return_value = True
        mock_lt_class.return_value = mock_processor
        
        # First call should create new processor
        processor1 = pipeline._LanguageAnalysisPipeline__get_language_tool_processor("de")
        
        # Second call should return cached processor
        processor2 = pipeline._LanguageAnalysisPipeline__get_language_tool_processor("de")
        
        assert processor1 is processor2
        assert "de-DE" in pipeline._language_tool_processors  # Should be normalized
        mock_lt_class.assert_called_once()
    
    def test_different_languages_create_different_processors(self):
        """Test that different languages create different processor instances."""
        pipeline = LanguageAnalysisPipeline()
        
        # Mock processors to avoid actual model loading
        with patch.object(pipeline, '_LanguageAnalysisPipeline__get_stanza_processor') as mock_get_stanza:
            with patch.object(pipeline, '_LanguageAnalysisPipeline__get_language_tool_processor') as mock_get_lt:
                mock_stanza_de = Mock()
                mock_stanza_en = Mock()
                mock_lt_de = Mock()
                mock_lt_en = Mock()
                
                mock_get_stanza.side_effect = lambda lang: mock_stanza_de if lang == "de" else mock_stanza_en
                mock_get_lt.side_effect = lambda lang: mock_lt_de if lang == "de" else mock_lt_en
                
                pipeline._is_initialized = True
                
                # Analyze German text
                request_de = AnalysisRequest(text="Das ist ein Test.", language="de")
                result_de = pipeline.analyze(request_de)
                
                # Analyze English text
                request_en = AnalysisRequest(text="This is a test.", language="en")
                result_en = pipeline.analyze(request_en)
                
                # Should have called get methods for both languages
                assert mock_get_stanza.call_count == 2
                assert mock_get_lt.call_count == 2
    
    def test_analyze_simple(self):
        """Test analyze_simple method."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        with patch.object(pipeline, 'analyze') as mock_analyze:
            mock_analyze.return_value = Mock()
            
            result = pipeline.analyze_simple("Test text", "de")
            
            mock_analyze.assert_called_once()
            call_args = mock_analyze.call_args[0][0]
            assert call_args.text == "Test text"
            assert call_args.language == "de"
            assert call_args.include_grammar_check is True
            assert call_args.include_morphological_analysis is True
            assert call_args.include_dependency_parsing is True
    
    def test_analyze_grammar_only_not_initialized(self):
        """Test analyze_grammar_only raises exception when not initialized."""
        pipeline = LanguageAnalysisPipeline()
        
        with pytest.raises(Exception, match="Pipeline not initialized. Call initialize\\(\\) first."):
            pipeline.analyze_grammar_only("Test text", "de")
    
    def test_analyze_grammar_only_success(self):
        """Test successful grammar-only analysis."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        mock_processor = Mock()
        mock_processor.check_grammar_only.return_value = []
        
        with patch.object(pipeline, '_LanguageAnalysisPipeline__get_language_tool_processor', return_value=mock_processor):
            result = pipeline.analyze_grammar_only("Test text", "de")
            
            mock_processor.check_grammar_only.assert_called_once_with("Test text")
            assert result == []
    
    def test_analyze_spelling_only_not_initialized(self):
        """Test analyze_spelling_only raises exception when not initialized."""
        pipeline = LanguageAnalysisPipeline()
        
        with pytest.raises(Exception, match="Pipeline not initialized. Call initialize\\(\\) first."):
            pipeline.analyze_spelling_only("Test text", "de")
    
    def test_analyze_spelling_only_success(self):
        """Test successful spelling-only analysis."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        mock_processor = Mock()
        mock_processor.check_spelling_only.return_value = []
        
        with patch.object(pipeline, '_LanguageAnalysisPipeline__get_language_tool_processor', return_value=mock_processor):
            result = pipeline.analyze_spelling_only("Test text", "de")
            
            mock_processor.check_spelling_only.assert_called_once_with("Test text")
            assert result == []
    
    def test_get_pipeline_status(self):
        """Test get_pipeline_status method."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        with patch.object(pipeline.model_manager, 'check_system_resources') as mock_resources:
            mock_resources.return_value = {"memory": "8GB"}
            
            status = pipeline.get_pipeline_status()
            
            assert status["initialized"] is True
            assert status["stanza_status"] == "No processors created"
            assert status["language_tool_status"] == "No processors created"
            assert status["cached_stanza_languages"] == []
            assert status["cached_language_tool_languages"] == []
            assert "supported_languages" in status
            assert "system_resources" in status
    
    def test_get_supported_languages(self):
        """Test get_supported_languages method."""
        pipeline = LanguageAnalysisPipeline()
        
        languages = pipeline.get_supported_languages()
        
        # Should return the supported languages from language constants
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "de-DE" in languages
        assert "en-US" in languages
    
    def test_is_language_supported(self):
        """Test is_language_supported method."""
        pipeline = LanguageAnalysisPipeline()
        
        # Test supported languages
        assert pipeline.is_language_supported("de") is True
        assert pipeline.is_language_supported("de-DE") is True
        assert pipeline.is_language_supported("en") is True
        assert pipeline.is_language_supported("en-US") is True
        
        # Test unsupported language
        assert pipeline.is_language_supported("xyz") is False
    
    def test_cleanup(self):
        """Test pipeline cleanup."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        # Add some mock processors to the cache
        mock_stanza_processor = Mock()
        mock_lt_processor = Mock()
        pipeline._stanza_processors["de"] = mock_stanza_processor
        pipeline._language_tool_processors["de-DE"] = mock_lt_processor
        
        with patch.object(pipeline.model_manager, 'cleanup_resources') as mock_cleanup:
            pipeline.cleanup()
            
            mock_stanza_processor.unload_model.assert_called_once()
            mock_lt_processor.unload_model.assert_called_once()
            mock_cleanup.assert_called_once()
            assert pipeline._is_initialized is False
            assert len(pipeline._stanza_processors) == 0
            assert len(pipeline._language_tool_processors) == 0
    
    def test_cleanup_with_exception(self):
        """Test pipeline cleanup with exception."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        # Add mock processor that will raise exception
        mock_processor = Mock()
        mock_processor.unload_model.side_effect = Exception("Cleanup failed")
        pipeline._stanza_processors["de"] = mock_processor
        
        # Should not raise exception - cleanup method catches exceptions
        pipeline.cleanup()
        
        # The cleanup method catches exceptions and logs them, but _is_initialized should still be False
        assert pipeline._is_initialized is False
    
    def test_get_performance_metrics(self):
        """Test get_performance_metrics method."""
        pipeline = LanguageAnalysisPipeline()
        
        with patch.object(pipeline.performance_monitor, 'get_performance_summary') as mock_perf:
            with patch.object(pipeline.cache, 'get_stats') as mock_cache:
                mock_perf.return_value = {"avg_time": 100}
                mock_cache.return_value = {"hits": 50}
                
                metrics = pipeline.get_performance_metrics()
                
                assert "performance" in metrics
                assert "cache" in metrics
                assert "pipeline_status" in metrics
                assert metrics["performance"] == {"avg_time": 100}
                assert metrics["cache"] == {"hits": 50}
    
    def test_clear_cache(self):
        """Test clear_cache method."""
        pipeline = LanguageAnalysisPipeline()
        
        with patch.object(pipeline.cache, 'clear') as mock_clear:
            pipeline.clear_cache()
            
            mock_clear.assert_called_once()
    
    def test_reset_performance_metrics(self):
        """Test reset_performance_metrics method."""
        pipeline = LanguageAnalysisPipeline()
        
        with patch.object(pipeline.performance_monitor, 'reset_metrics') as mock_reset:
            pipeline.reset_performance_metrics()
            
            mock_reset.assert_called_once()
