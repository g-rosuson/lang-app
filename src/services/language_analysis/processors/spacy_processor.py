"""
SpaCy Processor

This module provides SpaCy-based linguistic analysis including tokenization,
POS tagging, lemmatization, and morphological analysis for text.
"""

import time
from typing import List, Optional, Dict, Any
import spacy

from ..models.token_analysis import SpaCyToken, TokenAnalysis
from ...logging.logging import get_logger

logger = get_logger(__name__)


class SpaCyProcessor:
    """SpaCy-based linguistic analysis processor."""
    
    def __init__(self, model_name: str = "de_core_news_md"):
        """
        Initialize the SpaCy processor.
        
        Args:
            model_name (str): Name of the SpaCy model to use
        """
        self.model_name = model_name
        self.nlp: Optional[spacy.Language] = None
        self._is_loaded = False
        
    def load_model(self) -> None:
        """
        Load the SpaCy model.
        
        Raises:
            Exception: If model loading fails
        """
        try:
            logger.info(f"Loading SpaCy model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
            self._is_loaded = True
            logger.info(f"SpaCy model {self.model_name} loaded successfully")
        except OSError as e:
            logger.error(f"SpaCy model not found locally: {e}")
            raise Exception(f"Could not load SpaCy model {self.model_name}: {e}")
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self._is_loaded and self.nlp is not None
    
    def analyze(self, text: str) -> List[TokenAnalysis]:
        """
        Perform linguistic analysis using SpaCy.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[TokenAnalysis]: List of token analysis results
            
        Raises:
            Exception: If model is not loaded or analysis fails
        """
        if not self.is_loaded():
            raise Exception("SpaCy model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            start_time = time.time()
            
            # Process text with SpaCy
            doc = self.nlp(text)
            result = []
            
            for token in doc:
                # Extract token information
                token_data = TokenAnalysis(
                    text=token.text,
                    lemma=token.lemma_,
                    pos=token.pos_,
                    tag=token.tag_,
                    morph=token.morph.to_dict(),
                    processor="spacy"
                )
                result.append(token_data)
            
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"SpaCy analysis completed: {len(result)} tokens processed in {processing_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"SpaCy analysis failed: {e}")
            raise Exception(f"SpaCy analysis failed: {e}")
    
    def analyze_raw(self, text: str) -> List[SpaCyToken]:
        """
        Perform linguistic analysis and return raw SpaCy tokens.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[SpaCyToken]: List of raw SpaCy token results
        """
        if not self.is_loaded():
            raise Exception("SpaCy model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            # Process text with SpaCy
            doc = self.nlp(text)
            result = []
            
            for token in doc:
                token_data = SpaCyToken(
                    text=token.text,
                    lemma=token.lemma_,
                    pos=token.pos_,
                    tag=token.tag_,
                    morph=token.morph.to_dict()
                )
                result.append(token_data)
            
            logger.debug(f"SpaCy raw analysis completed: {len(result)} tokens processed")
            return result
            
        except Exception as e:
            logger.error(f"SpaCy raw analysis failed: {e}")
            raise Exception(f"SpaCy raw analysis failed: {e}")
    
    def get_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text using SpaCy.
        
        Args:
            text (str): The text to process
            
        Returns:
            List[str]: List of sentences
        """
        if not self.is_loaded():
            raise Exception("SpaCy model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
            logger.debug(f"Extracted {len(sentences)} sentences")
            return sentences
            
        except Exception as e:
            logger.error(f"Sentence extraction failed: {e}")
            return []
    
    def get_basic_stats(self, text: str) -> Dict[str, Any]:
        """
        Get basic text statistics using SpaCy.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, Any]: Basic text statistics
        """
        if not self.is_loaded():
            raise Exception("SpaCy model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "token_count": 0
            }
        
        try:
            doc = self.nlp(text)
            
            # Count tokens (excluding whitespace)
            tokens = [token for token in doc if not token.is_space]
            
            stats = {
                "word_count": len(tokens),
                "character_count": len(text),
                "sentence_count": len(list(doc.sents)),
                "token_count": len(tokens)
            }
            
            logger.debug(f"Basic stats calculated: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Basic stats calculation failed: {e}")
            return {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "token_count": 0
            }
    
    def unload_model(self) -> None:
        """Unload the SpaCy model to free memory."""
        if self.nlp is not None:
            self.nlp = None
            self._is_loaded = False
            logger.info("SpaCy model unloaded")
