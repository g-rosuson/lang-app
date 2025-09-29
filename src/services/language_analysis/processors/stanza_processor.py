"""
Stanza Processor

This module provides Stanza-based comprehensive linguistic analysis including
tokenization with character positions, POS tagging, lemmatization, morphological
analysis, and dependency parsing for multiple languages.
"""

import time
from typing import List, Optional, Dict, Any
import stanza

from ..models.analysis_result import Token, Sentence, MorphologyFeatures, DependencyRelation
from ...logging.logging import get_logger

logger = get_logger(__name__)


class StanzaProcessor:
    """Stanza-based comprehensive linguistic analysis processor."""
    
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
            language (str): Language code for Stanza (e.g., 'de', 'en', 'fr', 'es')
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
            logger.info(f"Loading Stanza pipeline for language: {self.language}")
            
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
            logger.info(f"Stanza pipeline loaded successfully for language: {self.language}")
            
        except Exception as e:
            logger.error(f"Failed to load Stanza pipeline for {self.language}: {e}")
            raise Exception(f"Could not initialize Stanza pipeline for {self.language}: {e}")
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self._is_loaded and self.nlp is not None
    
    def analyze_comprehensive(self, text: str) -> List[Sentence]:
        """
        Perform comprehensive linguistic analysis using Stanza with character positions,
        morphological analysis, and dependency parsing.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            List[Sentence]: List of sentence analyses with tokens
            
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
            sentences = []
            
            # Process each sentence
            for sentence in doc.sentences:
                tokens = []
                
                # Extract token information with character positions
                for word in sentence.words:
                    # Calculate character positions
                    start_char, end_char = self.__get_character_positions(text, word.text, word.id)
                    
                    # Extract morphological features
                    morphology = self.__extract_morphology(word)
                    
                    # Create dependency relation
                    dependency = DependencyRelation(
                        relation=word.deprel,
                        headTokenIndex=word.head - 1 if word.head > 0 else 0  # Convert to 0-based index
                    )
                    
                    # Create token with all information
                    token = Token(
                        text=word.text,
                        startChar=start_char,
                        endChar=end_char,
                        pos=word.upos,
                        lemma=word.lemma,
                        morphology=morphology,
                        dependency=dependency
                    )
                    tokens.append(token)
                
                # Create sentence with tokens
                sentence_obj = Sentence(
                    text=sentence.text,
                    tokens=tokens
                )
                sentences.append(sentence_obj)
            
            processing_time = (time.time() - start_time) * 1000
            total_tokens = sum(len(s.tokens) for s in sentences)
            logger.debug(f"Stanza comprehensive analysis completed: {len(sentences)} sentences, {total_tokens} tokens processed in {processing_time:.2f}ms")
            
            return sentences
            
        except Exception as e:
            logger.error(f"Stanza comprehensive analysis failed: {e}")
            raise Exception(f"Stanza comprehensive analysis failed: {e}")
    
    def __get_character_positions(self, text: str, token_text: str, token_id: int) -> tuple[int, int]:
        """
        Calculate character positions for a token in the original text.
        
        This is a simplified approach. For production use, you might want to use
        Stanza's built-in character position tracking if available.
        
        Args:
            text (str): Original text
            token_text (str): Token text to find
            token_id (int): Token ID in the sentence
            
        Returns:
            tuple[int, int]: Start and end character positions
        """
        # This is a simplified implementation
        # In practice, you might want to use Stanza's character position tracking
        # or implement a more sophisticated token-to-character mapping
        
        # Find the token in the text (this is a basic approach)
        start_pos = text.find(token_text)
        if start_pos != -1:
            return start_pos, start_pos + len(token_text)
        
        # Fallback: estimate position based on token ID
        # This is not accurate but provides a reasonable approximation
        words = text.split()
        if token_id <= len(words):
            estimated_start = len(' '.join(words[:token_id-1])) + (1 if token_id > 1 else 0)
            return estimated_start, estimated_start + len(token_text)
        
        return 0, len(token_text)
    
    def __extract_morphology(self, word) -> MorphologyFeatures:
        """
        Extract morphological features from a Stanza word.
        
        Args:
            word: Stanza word object
            
        Returns:
            MorphologyFeatures: Extracted morphological features
        """
        # Parse morphological features from Stanza's feats string
        features = {}
        additional_features = {}
        
        if hasattr(word, 'feats') and word.feats:
            # Stanza provides morphological features as a string like "Case=Nom|Gender=Masc|Number=Sing"
            for feat in word.feats.split('|'):
                if '=' in feat:
                    key, value = feat.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Map common morphological features
                    if key.lower() in ['case']:
                        features['Case'] = value
                    elif key.lower() in ['gender']:
                        features['Gender'] = value
                    elif key.lower() in ['number']:
                        features['Number'] = value
                    elif key.lower() in ['tense']:
                        features['Tense'] = value
                    elif key.lower() in ['person']:
                        features['Person'] = value
                    elif key.lower() in ['mood']:
                        features['Mood'] = value
                    elif key.lower() in ['voice']:
                        features['Voice'] = value
                    elif key.lower() in ['degree']:
                        features['Degree'] = value
                    else:
                        # Store language-specific features
                        additional_features[key] = value
        
        return MorphologyFeatures(
            Case=features.get('Case'),
            Gender=features.get('Gender'),
            Number=features.get('Number'),
            Tense=features.get('Tense'),
            Person=features.get('Person'),
            Mood=features.get('Mood'),
            Voice=features.get('Voice'),
            Degree=features.get('Degree'),
            additional_features=additional_features
        )
    
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
            logger.info(f"Stanza model unloaded for language: {self.language}")