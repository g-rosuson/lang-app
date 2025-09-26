"""
Language Analysis Pipeline

This module provides the main pipeline orchestrator that coordinates all
NLP processors and utilities for comprehensive text analysis.
"""

import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from .models.analysis_result import AnalysisResult, AnalysisRequest, ProcessingStats
from .processors.spacy_processor import SpaCyProcessor
from .processors.stanza_processor import StanzaProcessor
from .processors.spell_checker import SpellCheckerProcessor
from .utils.text_preprocessing import TextPreprocessor
from .utils.model_manager import ModelManager
from .utils.cache_manager import get_analysis_cache
from .utils.performance_monitor import get_performance_monitor
from ...services.logging.logging import get_logger

logger = get_logger(__name__)


class LanguageAnalysisPipeline:
    """Main pipeline orchestrator for language analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the language analysis pipeline.
        
        Args:
            config (Optional[Dict[str, Any]]): Pipeline configuration
        """
        self.config = config or {}
        self.text_preprocessor = TextPreprocessor(
            max_length=self.config.get('max_text_length', 10000)
        )
        self.model_manager = ModelManager()
        self.cache = get_analysis_cache()
        self.performance_monitor = get_performance_monitor()
        
        # Initialize processors
        self.spacy_processor = SpaCyProcessor(
            model_name=self.config.get('spacy_model', 'de_core_news_md')
        )
        self.stanza_processor = StanzaProcessor(
            language=self.config.get('stanza_language', 'de'),
            processors=self.config.get('stanza_processors', 'tokenize,mwt,pos,lemma,depparse'),
            model_dir=self.config.get('stanza_model_dir'),
            use_gpu=self.config.get('use_gpu', False)
        )
        self.spell_checker = SpellCheckerProcessor(
            language=self.config.get('spellcheck_language', 'de')
        )
        
        self._is_initialized = False
        self._initialization_errors = []
    
    def initialize(self) -> None:
        """
        Initialize all processors and load models.
        
        Raises:
            Exception: If initialization fails
        """
        logger.info("Initializing language analysis pipeline...")
        
        try:
            # Load models in sequence
            self.__load_spacy_model()
            self.__load_stanza_model()
            self.__load_spellchecker_model()
            
            self._is_initialized = True
            logger.info("Language analysis pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            self._initialization_errors.append(str(e))
            raise
    
    def is_initialized(self) -> bool:
        """Check if the pipeline is initialized and ready."""
        return self._is_initialized
    
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Perform comprehensive text analysis.
        
        Args:
            request (AnalysisRequest): Analysis request parameters
            
        Returns:
            AnalysisResult: Complete analysis results
            
        Raises:
            Exception: If analysis fails
        """
        if not self.is_initialized():
            raise Exception("Pipeline not initialized. Call initialize() first.")
        
        # Start performance monitoring
        request_metrics = self.performance_monitor.start_request(request.text)
        
        # Check cache first
        cached_result = self.cache.get(request.text, request.language)
        if cached_result:
            logger.info(f"Cache hit for text: '{request.text[:50]}...'")
            request_metrics.cache_hit = True
            self.performance_monitor.end_request(request_metrics, success=True, cache_hit=True)
            return AnalysisResult(**cached_result)
        
        start_time = time.time()
        errors = []
        
        try:
            # Preprocess text
            processed_text = self.text_preprocessor.preprocess(request.text)
            
            # Validate text
            validation = self.text_preprocessor.validate_text(processed_text)
            if not validation['valid']:
                raise ValueError(f"Text validation failed: {validation['message']}")
            
            # Get basic stats
            basic_stats = self.text_preprocessor.get_basic_stats(processed_text)
            
            # Initialize result
            result = AnalysisResult(
                text=processed_text,
                language=request.language or 'de',
                word_count=basic_stats['word_count'],
                character_count=basic_stats['character_count'],
                sentence_count=basic_stats['sentence_count']
            )
            
            # Run analyses based on request
            if request.include_spellcheck:
                try:
                    spellcheck_result = self.spell_checker.check_text(processed_text)
                    result.spellcheck = spellcheck_result
                except Exception as e:
                    logger.error(f"Spell check failed: {e}")
                    errors.append(f"Spell check failed: {e}")
            
            if request.include_spacy:
                try:
                    spacy_tokens = self.spacy_processor.analyze(processed_text)
                    result.spacy_tokens = spacy_tokens
                except Exception as e:
                    logger.error(f"SpaCy analysis failed: {e}")
                    errors.append(f"SpaCy analysis failed: {e}")
            
            if request.include_stanza:
                try:
                    stanza_tokens = self.stanza_processor.analyze(processed_text)
                    result.stanza_tokens = stanza_tokens
                except Exception as e:
                    logger.error(f"Stanza analysis failed: {e}")
                    errors.append(f"Stanza analysis failed: {e}")
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Create processing stats
            result.stats = ProcessingStats(
                processing_time_ms=round(processing_time, 2),
                tokens_processed=len(result.spacy_tokens) + len(result.stanza_tokens),
                words_checked=result.spellcheck.total_words if result.spellcheck else 0
            )
            
            # Set result status
            result.success = len(errors) == 0
            result.errors = errors
            
            # Cache the result
            self.cache.set(request.text, result.model_dump(), request.language)
            
            # End performance monitoring
            self.performance_monitor.end_request(request_metrics, success=result.success, cache_hit=False)
            
            logger.info(f"Analysis completed in {processing_time:.2f}ms with {len(errors)} errors")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def analyze_simple(self, text: str) -> AnalysisResult:
        """
        Perform simple analysis with default settings.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            AnalysisResult: Analysis results
        """
        request = AnalysisRequest(
            text=text,
            language='de',
            include_spellcheck=True,
            include_spacy=True,
            include_stanza=True
        )
        return self.analyze(request)
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current status of the pipeline.
        
        Returns:
            Dict[str, Any]: Pipeline status information
        """
        return {
            "initialized": self.is_initialized(),
            "spacy_loaded": self.spacy_processor.is_loaded(),
            "stanza_loaded": self.stanza_processor.is_loaded(),
            "spellcheck_loaded": self.spell_checker.is_loaded(),
            "initialization_errors": self._initialization_errors,
            "system_resources": self.model_manager.check_system_resources()
        }
    
    def cleanup(self) -> None:
        """Clean up resources and unload models."""
        logger.info("Cleaning up pipeline resources...")
        
        try:
            self.spacy_processor.unload_model()
            self.stanza_processor.unload_model()
            self.spell_checker.unload_model()
            self.model_manager.cleanup_resources()
            
            self._is_initialized = False
            logger.info("Pipeline cleanup completed")
            
        except Exception as e:
            logger.error(f"Pipeline cleanup failed: {e}")
    
    # Private methods for model loading
    def __load_spacy_model(self) -> None:
        """Load SpaCy model."""
        try:
            self.spacy_processor.load_model()
            logger.info("SpaCy model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SpaCy model: {e}")
            raise
    
    def __load_stanza_model(self) -> None:
        """Load Stanza model."""
        try:
            self.stanza_processor.load_model()
            logger.info("Stanza model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Stanza model: {e}")
            raise
    
    def __load_spellchecker_model(self) -> None:
        """Load spell checker model."""
        try:
            self.spell_checker.load_model()
            logger.info("Spell checker model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spell checker model: {e}")
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics and cache statistics.
        
        Returns:
            Dict[str, Any]: Performance metrics including cache stats, processing times, etc.
        """
        return {
            "performance": self.performance_monitor.get_performance_summary(),
            "cache": self.cache.get_stats(),
            "pipeline_status": {
                "initialized": self.is_initialized(),
                "config": self.config
            }
        }
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self.cache.clear()
        logger.info("Analysis cache cleared")
    
    def reset_performance_metrics(self) -> None:
        """Reset performance monitoring metrics."""
        self.performance_monitor.reset_metrics()
        logger.info("Performance metrics reset")
    
    def __del__(self):
        """Cleanup when the pipeline is destroyed."""
        self.cleanup()


# Global pipeline instance (singleton pattern)
_pipeline_instance: Optional[LanguageAnalysisPipeline] = None


def get_language_analysis_service(config: Optional[Dict[str, Any]] = None) -> LanguageAnalysisPipeline:
    """
    Get the global language analysis service instance.
    
    This function implements the singleton pattern to ensure only one
    instance of the pipeline exists throughout the application lifecycle.
    
    Args:
        config (Optional[Dict[str, Any]]): Pipeline configuration
        
    Returns:
        LanguageAnalysisPipeline: The global pipeline instance
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = LanguageAnalysisPipeline(config)
    return _pipeline_instance


def initialize_pipeline(config: Optional[Dict[str, Any]] = None) -> LanguageAnalysisPipeline:
    """
    Initialize the global pipeline with the given configuration.
    
    Args:
        config (Optional[Dict[str, Any]]): Pipeline configuration
        
    Returns:
        LanguageAnalysisPipeline: The initialized pipeline instance
    """
    pipeline = get_language_analysis_service(config)
    if not pipeline.is_initialized():
        pipeline.initialize()
    return pipeline
