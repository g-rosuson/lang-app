"""
Language Analysis Pipeline

This module provides the main pipeline orchestrator that coordinates Stanza
and LanguageTool processors for comprehensive text analysis with character
positions, morphological analysis, dependency parsing, and grammar/spell checking.
"""

import time
from typing import Optional, Dict, Any, List

from .models.analysis_result import AnalysisResult, AnalysisRequest, GrammarError
from .processors.stanza_processor import StanzaProcessor
from .processors.language_tool_processor import LanguageToolProcessor
from .utils.text_preprocessing import TextPreprocessor
from .utils.model_manager import ModelManager
from .utils.cache_manager import get_analysis_cache
from .utils.performance_monitor import get_performance_monitor
from ...services.logging.logging import get_logger

logger = get_logger(__name__)


class LanguageAnalysisPipeline:
    """Main pipeline orchestrator for comprehensive language analysis."""
    
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
        self.stanza_processor = StanzaProcessor(
            language=self.config.get('stanza_language', 'de'),
            processors=self.config.get('stanza_processors', 'tokenize,mwt,pos,lemma,depparse'),
            model_dir=self.config.get('stanza_model_dir'),
            use_gpu=self.config.get('use_gpu', False)
        )
        self.language_tool_processor = LanguageToolProcessor(
            language=self.config.get('language_tool_language', 'de')
        )
        
        self._is_initialized = False
        self._initialization_errors = []
    
    def initialize(self) -> None:
        """
        Initialize all processors and load models.
        
        Raises:
            Exception: If initialization fails
        """
        logger.info("Initializing comprehensive language analysis pipeline...")
        
        try:
            # Load models in sequence
            self.__load_stanza_model()
            self.__load_language_tool_model()
            
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
        Perform comprehensive text analysis with Stanza and LanguageTool.
        
        Args:
            request (AnalysisRequest): Analysis request parameters
            
        Returns:
            AnalysisResult: Complete analysis results matching the required JSON structure
            
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
        processing_time = 0.0  # Initialize processing time
        errors = []
        
        try:
            # Preprocess text
            processed_text = self.text_preprocessor.preprocess(request.text)
            
            # Validate text
            validation = self.text_preprocessor.validate_text(processed_text)
            if not validation['valid']:
                raise ValueError(f"Text validation failed: {validation['message']}")
            
            # Initialize result with required JSON structure
            result = AnalysisResult(
                originalText=processed_text,
                language=request.language,
                sentences=[],
                errors=[]
            )
            
            # Run Stanza analysis for comprehensive linguistic analysis
            if request.include_morphological_analysis or request.include_dependency_parsing:
                try:
                    logger.info("Running Stanza comprehensive analysis...")
                    sentences = self.stanza_processor.analyze_comprehensive(processed_text)
                    result.sentences = sentences
                    logger.info(f"Stanza analysis completed: {len(sentences)} sentences processed")
                except Exception as e:
                    logger.error(f"Stanza analysis failed: {e}")
                    errors.append(f"Stanza analysis failed: {e}")
            
            # Run LanguageTool analysis for grammar and spell checking
            if request.include_grammar_check:
                try:
                    logger.info("Running LanguageTool grammar and spell checking...")
                    grammar_errors = self.language_tool_processor.check_text(processed_text)
                    result.errors = grammar_errors
                    logger.info(f"LanguageTool analysis completed: {len(grammar_errors)} errors found")
                except Exception as e:
                    logger.error(f"LanguageTool analysis failed: {e}")
                    errors.append(f"LanguageTool analysis failed: {e}")
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Log completion
            total_tokens = sum(len(s.tokens) for s in result.sentences)
            logger.info(f"Analysis completed in {processing_time:.2f}ms: {len(result.sentences)} sentences, {total_tokens} tokens, {len(result.errors)} errors")
            
            # Cache the result
            self.cache.set(request.text, result.model_dump(), request.language)
            
            # End performance monitoring
            self.performance_monitor.end_request(request_metrics, success=len(errors) == 0, cache_hit=False)
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # End performance monitoring even on failure
            self.performance_monitor.end_request(request_metrics, success=False, cache_hit=False, error_message=str(e))
            raise
    
    def analyze_simple(self, text: str, language: str = "de") -> AnalysisResult:
        """
        Perform simple analysis with default settings.
        
        Args:
            text (str): Text to analyze
            language (str): Language code for analysis
            
        Returns:
            AnalysisResult: Analysis results
        """
        request = AnalysisRequest(
            text=text,
            language=language,
            include_grammar_check=True,
            include_morphological_analysis=True,
            include_dependency_parsing=True
        )
        return self.analyze(request)
    
    def analyze_grammar_only(self, text: str, language: str = "de") -> List[GrammarError]:
        """
        Perform grammar checking only.
        
        Args:
            text (str): Text to analyze
            language (str): Language code for analysis
            
        Returns:
            List[GrammarError]: Grammar errors found
        """
        if not self.is_initialized():
            raise Exception("Pipeline not initialized. Call initialize() first.")
        
        try:
            # Update language if different
            if self.language_tool_processor.language != language:
                self.language_tool_processor.language = language
                self.language_tool_processor.load_model()
            
            return self.language_tool_processor.check_grammar_only(text)
            
        except Exception as e:
            logger.error(f"Grammar analysis failed: {e}")
            raise
    
    def analyze_spelling_only(self, text: str, language: str = "de") -> List[GrammarError]:
        """
        Perform spelling checking only.
        
        Args:
            text (str): Text to analyze
            language (str): Language code for analysis
            
        Returns:
            List[GrammarError]: Spelling errors found
        """
        if not self.is_initialized():
            raise Exception("Pipeline not initialized. Call initialize() first.")
        
        try:
            # Update language if different
            if self.language_tool_processor.language != language:
                self.language_tool_processor.language = language
                self.language_tool_processor.load_model()
            
            return self.language_tool_processor.check_spelling_only(text)
            
        except Exception as e:
            logger.error(f"Spelling analysis failed: {e}")
            raise
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current status of the pipeline.
        
        Returns:
            Dict[str, Any]: Pipeline status information
        """
        return {
            "initialized": self.is_initialized(),
            "stanza_loaded": self.stanza_processor.is_loaded(),
            "language_tool_loaded": self.language_tool_processor.is_loaded(),
            "stanza_language": self.stanza_processor.language,
            "language_tool_language": self.language_tool_processor.language,
            "supported_languages": self.language_tool_processor.get_supported_languages(),
            "initialization_errors": self._initialization_errors,
            "system_resources": self.model_manager.check_system_resources()
        }
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List[str]: List of supported language codes
        """
        return self.language_tool_processor.get_supported_languages()
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language (str): Language code to check
            
        Returns:
            bool: True if language is supported, False otherwise
        """
        return self.language_tool_processor.is_language_supported(language)
    
    def cleanup(self) -> None:
        """Clean up resources and unload models."""
        logger.info("Cleaning up pipeline resources...")
        
        try:
            self.stanza_processor.unload_model()
            self.language_tool_processor.unload_model()
            self.model_manager.cleanup_resources()
            
            self._is_initialized = False
            logger.info("Pipeline cleanup completed")
            
        except Exception as e:
            logger.error(f"Pipeline cleanup failed: {e}")
    
    # Private methods for model loading
    def __load_stanza_model(self) -> None:
        """Load Stanza model."""
        try:
            self.stanza_processor.load_model()
            logger.info(f"Stanza model loaded successfully for language: {self.stanza_processor.language}")
        except Exception as e:
            logger.error(f"Failed to load Stanza model: {e}")
            raise
    
    def __load_language_tool_model(self) -> None:
        """Load LanguageTool model."""
        try:
            self.language_tool_processor.load_model()
            logger.info(f"LanguageTool loaded successfully for language: {self.language_tool_processor.language}")
        except Exception as e:
            logger.error(f"Failed to load LanguageTool model: {e}")
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