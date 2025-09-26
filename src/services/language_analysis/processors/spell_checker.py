"""
Spell Checker Processor

This module provides German spell checking functionality using PySpellChecker
with misspelled word detection and correction suggestions.
"""

import time
from typing import List, Optional, Dict, Any
from spellchecker import SpellChecker

from ..models.spellcheck_result import SpellCheckResult, SpellCheckSummary
from ...logging.logging import get_logger

logger = get_logger(__name__)


class SpellCheckerProcessor:
    """German spell checking processor using PySpellChecker."""
    
    def __init__(self, language: str = "de"):
        """
        Initialize the spell checker processor.
        
        Args:
            language (str): Language code for spell checking
        """
        self.language = language
        self.spell: Optional[SpellChecker] = None
        self._is_loaded = False
        
    def load_model(self) -> None:
        """
        Load the spell checker with language support.
        
        Raises:
            Exception: If spell checker initialization fails
        """
        try:
            logger.info(f"Loading spell checker for language: {self.language}")
            self.spell = SpellChecker(language=self.language)
            self._is_loaded = True
            logger.info("Spell checker loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load spell checker: {e}")
            raise Exception(f"Could not initialize spell checker: {e}")
    
    def is_loaded(self) -> bool:
        """Check if the spell checker is loaded and ready."""
        return self._is_loaded and self.spell is not None
    
    def check_text(self, text: str) -> SpellCheckSummary:
        """
        Perform spell checking on the input text.
        
        Args:
            text (str): The text to check for spelling errors
            
        Returns:
            SpellCheckSummary: Complete spell checking results
            
        Raises:
            Exception: If spell checker is not loaded or checking fails
        """
        if not self.is_loaded():
            raise Exception("Spell checker not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return SpellCheckSummary(
                misspelled_words={},
                total_misspelled=0,
                total_words=0,
                accuracy=100.0
            )
        
        try:
            start_time = time.time()
            
            # Split text into words and clean them
            words = self.__extract_words(text)
            if not words:
                return SpellCheckSummary(
                    misspelled_words={},
                    total_misspelled=0,
                    total_words=0,
                    accuracy=100.0
                )
            
            # Find misspelled words
            misspelled = self.spell.unknown(words)
            misspelled_words = {}
            
            # Get correction candidates for each misspelled word
            for word in misspelled:
                candidates = self.spell.candidates(word)
                if candidates:
                    misspelled_words[word] = list(candidates)
            
            # Calculate statistics
            total_words = len(words)
            total_misspelled = len(misspelled_words)
            accuracy = ((total_words - total_misspelled) / total_words * 100) if total_words > 0 else 100.0
            
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"Spell check completed: {total_misspelled} misspelled words found in {processing_time:.2f}ms")
            
            return SpellCheckSummary(
                misspelled_words=misspelled_words,
                total_misspelled=total_misspelled,
                total_words=total_words,
                accuracy=round(accuracy, 2)
            )
            
        except Exception as e:
            logger.error(f"Spell check failed: {e}")
            raise Exception(f"Spell check failed: {e}")
    
    def check_word(self, word: str) -> Optional[SpellCheckResult]:
        """
        Check a single word for spelling errors.
        
        Args:
            word (str): The word to check
            
        Returns:
            Optional[SpellCheckResult]: Spell check result if word is misspelled, None otherwise
        """
        if not self.is_loaded():
            raise Exception("Spell checker not loaded. Call load_model() first.")
        
        if not word or not word.strip():
            return None
        
        try:
            # Clean the word
            clean_word = word.strip().lower()
            if not clean_word:
                return None
            
            # Check if word is misspelled
            if clean_word in self.spell:
                return None  # Word is correctly spelled
            
            # Get correction candidates
            candidates = self.spell.candidates(clean_word)
            if not candidates:
                return None
            
            return SpellCheckResult(
                word=word,
                candidates=list(candidates),
                confidence=None  # PySpellChecker doesn't provide confidence scores
            )
            
        except Exception as e:
            logger.error(f"Single word spell check failed: {e}")
            return None
    
    def get_corrections(self, word: str) -> List[str]:
        """
        Get correction suggestions for a misspelled word.
        
        Args:
            word (str): The misspelled word
            
        Returns:
            List[str]: List of correction suggestions
        """
        if not self.is_loaded():
            raise Exception("Spell checker not loaded. Call load_model() first.")
        
        if not word or not word.strip():
            return []
        
        try:
            clean_word = word.strip().lower()
            if not clean_word:
                return []
            
            candidates = self.spell.candidates(clean_word)
            return list(candidates) if candidates else []
            
        except Exception as e:
            logger.error(f"Getting corrections failed: {e}")
            return []
    
    def is_correct(self, word: str) -> bool:
        """
        Check if a word is spelled correctly.
        
        Args:
            word (str): The word to check
            
        Returns:
            bool: True if word is correctly spelled, False otherwise
        """
        if not self.is_loaded():
            raise Exception("Spell checker not loaded. Call load_model() first.")
        
        if not word or not word.strip():
            return True
        
        try:
            clean_word = word.strip().lower()
            if not clean_word:
                return True
            
            return clean_word in self.spell
            
        except Exception as e:
            logger.error(f"Spelling correctness check failed: {e}")
            return True  # Assume correct on error
    
    def __extract_words(self, text: str) -> List[str]:
        """
        Extract words from text for spell checking.
        
        Args:
            text (str): The text to extract words from
            
        Returns:
            List[str]: List of words
        """
        if not text:
            return []
        
        # Simple word extraction - split on whitespace and remove punctuation
        words = []
        for word in text.split():
            # Remove common punctuation but keep German-specific characters
            clean_word = ''.join(char for char in word if char.isalnum() or char in 'äöüßÄÖÜ')
            if clean_word and len(clean_word) > 1:  # Skip single characters
                words.append(clean_word.lower())
        
        return words
    
    def get_dictionary_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary information
        """
        if not self.is_loaded():
            return {"error": "Spell checker not loaded"}
        
        try:
            return {
                "language": self.language,
                "word_count": len(self.spell),
                "loaded": True
            }
        except Exception as e:
            logger.error(f"Failed to get dictionary info: {e}")
            return {"error": str(e)}
    
    def unload_model(self) -> None:
        """Unload the spell checker to free memory."""
        if self.spell is not None:
            self.spell = None
            self._is_loaded = False
            logger.info("Spell checker unloaded")
