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
        assert pipeline.stanza_processor.language == 'de'
        assert pipeline.language_tool_processor.language == 'de'
        assert pipeline._is_initialized is False
        assert pipeline._initialization_errors == []
    
    def test_pipeline_initialization_defaults(self):
        """Test pipeline initialization with default config."""
        pipeline = LanguageAnalysisPipeline()
        
        assert pipeline.config == {}
        assert pipeline.stanza_processor.language == 'de'
        assert pipeline.language_tool_processor.language == 'de'
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
    
    @patch.object(LanguageAnalysisPipeline, '_LanguageAnalysisPipeline__load_stanza_model')
    @patch.object(LanguageAnalysisPipeline, '_LanguageAnalysisPipeline__load_language_tool_model')
    def test_initialize_success(self, mock_load_lt, mock_load_stanza):
        """Test successful pipeline initialization."""
        pipeline = LanguageAnalysisPipeline()
        
        pipeline.initialize()
        
        mock_load_stanza.assert_called_once()
        mock_load_lt.assert_called_once()
        assert pipeline._is_initialized is True
    
    @patch.object(LanguageAnalysisPipeline, '_LanguageAnalysisPipeline__load_stanza_model')
    def test_initialize_stanza_failure(self, mock_load_stanza):
        """Test pipeline initialization failure due to Stanza."""
        pipeline = LanguageAnalysisPipeline()
        mock_load_stanza.side_effect = Exception("Stanza loading failed")
        
        with pytest.raises(Exception, match="Stanza loading failed"):
            pipeline.initialize()
        
        assert pipeline._is_initialized is False
        assert len(pipeline._initialization_errors) == 1
        assert "Stanza loading failed" in pipeline._initialization_errors[0]
    
    @patch.object(LanguageAnalysisPipeline, '_LanguageAnalysisPipeline__load_stanza_model')
    @patch.object(LanguageAnalysisPipeline, '_LanguageAnalysisPipeline__load_language_tool_model')
    def test_initialize_language_tool_failure(self, mock_load_lt, mock_load_stanza):
        """Test pipeline initialization failure due to LanguageTool."""
        pipeline = LanguageAnalysisPipeline()
        mock_load_lt.side_effect = Exception("LanguageTool loading failed")
        
        with pytest.raises(Exception, match="LanguageTool loading failed"):
            pipeline.initialize()
        
        assert pipeline._is_initialized is False
        assert len(pipeline._initialization_errors) == 1
        assert "LanguageTool loading failed" in pipeline._initialization_errors[0]
    
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
        
        # Mock processors
        with patch.object(pipeline.stanza_processor, 'analyze_comprehensive') as mock_stanza:
            with patch.object(pipeline.language_tool_processor, 'check_text') as mock_lt:
                mock_stanza.return_value = []
                mock_lt.return_value = []
                
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
        
        with patch.object(pipeline.language_tool_processor, 'check_grammar_only') as mock_check:
            mock_check.return_value = []
            
            result = pipeline.analyze_grammar_only("Test text", "de")
            
            mock_check.assert_called_once_with("Test text")
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
        
        with patch.object(pipeline.language_tool_processor, 'check_spelling_only') as mock_check:
            mock_check.return_value = []
            
            result = pipeline.analyze_spelling_only("Test text", "de")
            
            mock_check.assert_called_once_with("Test text")
            assert result == []
    
    def test_get_pipeline_status(self):
        """Test get_pipeline_status method."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        with patch.object(pipeline.stanza_processor, 'is_loaded') as mock_stanza_loaded:
            with patch.object(pipeline.language_tool_processor, 'is_loaded') as mock_lt_loaded:
                with patch.object(pipeline.model_manager, 'check_system_resources') as mock_resources:
                    mock_stanza_loaded.return_value = True
                    mock_lt_loaded.return_value = True
                    mock_resources.return_value = {"memory": "8GB"}
                    
                    status = pipeline.get_pipeline_status()
                    
                    assert status["initialized"] is True
                    assert status["stanza_loaded"] is True
                    assert status["language_tool_loaded"] is True
                    assert status["stanza_language"] == "de"
                    assert status["language_tool_language"] == "de"
                    assert "supported_languages" in status
                    assert "system_resources" in status
    
    def test_get_supported_languages(self):
        """Test get_supported_languages method."""
        pipeline = LanguageAnalysisPipeline()
        
        with patch.object(pipeline.language_tool_processor, 'get_supported_languages') as mock_get_langs:
            mock_get_langs.return_value = ["de", "en", "fr"]
            
            languages = pipeline.get_supported_languages()
            
            assert languages == ["de", "en", "fr"]
            mock_get_langs.assert_called_once()
    
    def test_is_language_supported(self):
        """Test is_language_supported method."""
        pipeline = LanguageAnalysisPipeline()
        
        with patch.object(pipeline.language_tool_processor, 'is_language_supported') as mock_is_supported:
            mock_is_supported.return_value = True
            
            result = pipeline.is_language_supported("de")
            
            assert result is True
            mock_is_supported.assert_called_once_with("de")
    
    def test_cleanup(self):
        """Test pipeline cleanup."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        with patch.object(pipeline.stanza_processor, 'unload_model') as mock_stanza_unload:
            with patch.object(pipeline.language_tool_processor, 'unload_model') as mock_lt_unload:
                with patch.object(pipeline.model_manager, 'cleanup_resources') as mock_cleanup:
                    pipeline.cleanup()
                    
                    mock_stanza_unload.assert_called_once()
                    mock_lt_unload.assert_called_once()
                    mock_cleanup.assert_called_once()
                    assert pipeline._is_initialized is False
    
    def test_cleanup_with_exception(self):
        """Test pipeline cleanup with exception."""
        pipeline = LanguageAnalysisPipeline()
        pipeline._is_initialized = True
        
        with patch.object(pipeline.stanza_processor, 'unload_model', side_effect=Exception("Cleanup failed")):
            # Should not raise exception
            pipeline.cleanup()
            
            # The cleanup method catches exceptions and logs them, but _is_initialized remains True due to exception
            assert pipeline._is_initialized is True
    
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
