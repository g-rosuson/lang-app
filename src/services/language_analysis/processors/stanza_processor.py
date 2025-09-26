"""
Stanza Processor

This module provides Stanza-based advanced linguistic analysis including
dependency parsing, POS tagging, and lemmatization for text.
"""

import time
from typing import List, Optional, Dict, Any
import stanza

from ..models.token_analysis import StanzaToken, TokenAnalysis
from ...logging.logging import get_logger

logger = get_logger(__name__)


class StanzaProcessor:
    """Stanza-based advanced linguistic analysis processor."""
    
    def __init__(
        self, 
        language: str = "de",
        processors: str = "tokenize,mwt,pos,lemma,depparse",
        model_dir: Optional[str] = None,
        use_gpu: bool = False
    ):
        """
        Initialize the Stanza processor.
        
        Args:
            language (str): Language code for Stanza
            processors (str): Comma-separated list of processors
            model_dir (Optional[str]): Directory for Stanza models
            use_gpu (bool): Whether to use GPU for processing
        """
        self.language = language
        self.processors = processors
        self.model_dir = model_dir
        self.use_gpu = use_gpu
        self.nlp: Optional[stanza.Pipeline] = None
        self._is_loaded = False
        
    def load_model(self) -> None:
        """
        Load the Stanza language pipeline.
        
        Raises:
            Exception: If Stanza pipeline initialization fails
        """
        try:
            logger.info("Loading Stanza pipeline...")
            
            # Prepare pipeline arguments
            pipeline_args = {
                "lang": self.language,
                "processors": self.processors,
                "use_gpu": self.use_gpu,
                "verbose": False
            }
            
            # Add model directory if specified
            if self.model_dir:
                pipeline_args["model_dir"] = str(self.model_dir)
            
            self.nlp = stanza.Pipeline(**pipeline_args)
            self._is_loaded = True
            logger.info("Stanza pipeline loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Stanza pipeline: {e}")
            raise Exception(f"Could not initialize Stanza pipeline: {e}")
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self._is_loaded and self.nlp is not None
    
    def analyze(self, text: str) -> List[TokenAnalysis]:
        """
        Perform linguistic analysis using Stanza.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[TokenAnalysis]: List of token analysis results
            
        Raises:
            Exception: If model is not loaded or analysis fails
        """
        if not self.is_loaded():
            raise Exception("Stanza model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            start_time = time.time()
            
            # Process text with Stanza
            doc = self.nlp(text)
            result = []
            
            # Extract token information from all sentences
            for sentence in doc.sentences:
                for word in sentence.words:
                    token_data = TokenAnalysis(
                        text=word.text,
                        lemma=word.lemma,
                        pos=word.upos,
                        tag=word.xpos,
                        head=word.head,
                        deprel=word.deprel,
                        processor="stanza"
                    )
                    result.append(token_data)
            
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"Stanza analysis completed: {len(result)} tokens processed in {processing_time:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Stanza analysis failed: {e}")
            raise Exception(f"Stanza analysis failed: {e}")
    
    def analyze_raw(self, text: str) -> List[StanzaToken]:
        """
        Perform linguistic analysis and return raw Stanza tokens.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[StanzaToken]: List of raw Stanza token results
        """
        if not self.is_loaded():
            raise Exception("Stanza model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            # Process text with Stanza
            doc = self.nlp(text)
            result = []
            
            # Extract token information from all sentences
            for sentence in doc.sentences:
                for word in sentence.words:
                    token_data = StanzaToken(
                        text=word.text,
                        lemma=word.lemma,
                        upos=word.upos,
                        xpos=word.xpos,
                        head=word.head,
                        deprel=word.deprel
                    )
                    result.append(token_data)
            
            logger.debug(f"Stanza raw analysis completed: {len(result)} tokens processed")
            return result
            
        except Exception as e:
            logger.error(f"Stanza raw analysis failed: {e}")
            raise Exception(f"Stanza raw analysis failed: {e}")
    
    def get_dependency_tree(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract dependency tree information from text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[Dict[str, Any]]: List of dependency tree nodes
        """
        if not self.is_loaded():
            raise Exception("Stanza model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            doc = self.nlp(text)
            tree_nodes = []
            
            for sentence in doc.sentences:
                for word in sentence.words:
                    node = {
                        "id": word.id,
                        "text": word.text,
                        "lemma": word.lemma,
                        "upos": word.upos,
                        "xpos": word.xpos,
                        "head": word.head,
                        "deprel": word.deprel,
                        "sentence_id": len(tree_nodes)  # Simple sentence tracking
                    }
                    tree_nodes.append(node)
            
            logger.debug(f"Dependency tree extracted: {len(tree_nodes)} nodes")
            return tree_nodes
            
        except Exception as e:
            logger.error(f"Dependency tree extraction failed: {e}")
            return []
    
    def get_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text using Stanza.
        
        Args:
            text (str): The text to process
            
        Returns:
            List[str]: List of sentences
        """
        if not self.is_loaded():
            raise Exception("Stanza model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sentences if sent.text.strip()]
            logger.debug(f"Extracted {len(sentences)} sentences")
            return sentences
            
        except Exception as e:
            logger.error(f"Sentence extraction failed: {e}")
            return []
    
    def get_basic_stats(self, text: str) -> Dict[str, Any]:
        """
        Get basic text statistics using Stanza.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, Any]: Basic text statistics
        """
        if not self.is_loaded():
            raise Exception("Stanza model not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return {
                "word_count": 0,
                "character_count": 0,
                "sentence_count": 0,
                "token_count": 0
            }
        
        try:
            doc = self.nlp(text)
            
            # Count words and tokens
            words = []
            for sentence in doc.sentences:
                words.extend([word.text for word in sentence.words])
            
            stats = {
                "word_count": len(words),
                "character_count": len(text),
                "sentence_count": len(doc.sentences),
                "token_count": len(words)
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
        """Unload the Stanza model to free memory."""
        if self.nlp is not None:
            self.nlp = None
            self._is_loaded = False
            logger.info("Stanza model unloaded")
