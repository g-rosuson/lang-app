"""
LanguageTool Processor

This module provides LanguageTool-based grammar and spell checking functionality
for multiple languages with comprehensive error extraction including character
positions, suggestions, and rule IDs.
"""

import time
from typing import List, Optional, Dict
import language_tool_python

from ..models.analysis_result import GrammarError
from ..models.language_constants import language_constants
from ...logging.logging import get_logger

logger = get_logger(__name__)


class LanguageToolProcessor:
    """LanguageTool-based grammar and spell checking processor."""
    
    def __init__(self, language: str = "de"):
        """
        Initialize the LanguageTool processor.
        
        Args:
            language (str): Language code for LanguageTool (e.g., 'de', 'en', 'fr', 'es')
                          Will be converted to proper format (e.g., 'de-DE', 'en-US')
        """
        self.language = language_constants.normalize_language_code(language)
        self.tool: Optional[language_tool_python.LanguageTool] = None
        self._is_loaded = False
        
    def load_model(self) -> None:
        """
        Load the LanguageTool with language support.
        
        Raises:
            Exception: If LanguageTool initialization fails
        """
        try:
            logger.info(f"Loading LanguageTool for language: {self.language}")
            
            # Set up Hunspell path if available
            import os
            hunspell_path = os.environ.get('LT_HUNSPELL_DICT_PATH', '/usr/share/hunspell')
            if os.path.exists(hunspell_path):
                logger.info(f"Hunspell dictionaries found at: {hunspell_path}")
            else:
                logger.warning(f"Hunspell dictionaries not found at: {hunspell_path}")
            
            # Initialize LanguageTool with the specified language
            self.tool = language_tool_python.LanguageTool(self.language)
            self._is_loaded = True
            logger.info(f"LanguageTool loaded successfully for language: {self.language}")
            
        except Exception as e:
            logger.error(f"Failed to load LanguageTool for {self.language}: {e}")
            if "HunspellLibrary" in str(e):
                logger.error("Hunspell library error detected. Make sure Hunspell dictionaries are installed.")
                logger.error("Try: apt-get install libhunspell-dev hunspell-de-de hunspell-en-us")
            raise Exception(f"Could not initialize LanguageTool for {self.language}: {e}")
    
    def is_loaded(self) -> bool:
        """Check if LanguageTool is loaded and ready."""
        return self._is_loaded and self.tool is not None
    
    def check_text(self, text: str) -> List[GrammarError]:
        """
        Perform comprehensive grammar and spell checking on the input text.
        
        Args:
            text (str): The text to check for grammar and spelling errors
            
        Returns:
            List[GrammarError]: List of grammar and spelling errors found
            
        Raises:
            Exception: If LanguageTool is not loaded or checking fails
        """
        if not self.is_loaded():
            raise Exception("LanguageTool not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            start_time = time.time()
            
            # Preprocess text to make it more LanguageTool-friendly
            processed_text = self.__preprocess_text_for_languagetool(text)
            
            # Check text for grammar and spelling errors
            matches = self.tool.check(processed_text)
            errors = []
            
            # Process each match and extract error information
            for match in matches:
                error = self.__extract_error_info(match, processed_text)
                if error:
                    # Adjust character positions back to original text if needed
                    error = self.__adjust_error_positions(error, text, processed_text)
                    if error:
                        errors.append(error)
            
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"LanguageTool check completed: {len(errors)} errors found in {processing_time:.2f}ms")
            
            return errors
            
        except Exception as e:
            logger.warning(f"LanguageTool check failed for text '{text[:50]}...': {e}")
            # Try fallback: check individual words for spelling errors
            try:
                return self.__fallback_spell_check(text)
            except Exception as fallback_error:
                logger.warning(f"Fallback spell check also failed: {fallback_error}")
                # Return empty list instead of raising exception to prevent pipeline failure
                return []
    
    def __preprocess_text_for_languagetool(self, text: str) -> str:
        """
        Preprocess text to make it more LanguageTool-friendly.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Preprocessed text
        """
        # Replace problematic patterns that cause LanguageTool to crash
        processed = text
        
        # Replace repeated numbers with single numbers (e.g., "5 5" -> "5")
        import re
        processed = re.sub(r'(\d+)\s+\1', r'\1', processed)
        
        # Replace mixed language patterns that might confuse LanguageTool
        # Keep the text mostly intact but make it more consistent
        
        return processed
    
    def __adjust_error_positions(self, error: GrammarError, original_text: str, processed_text: str) -> Optional[GrammarError]:
        """
        Adjust error character positions if text was preprocessed.
        
        Args:
            error (GrammarError): Error with positions in processed text
            original_text (str): Original text
            processed_text (str): Processed text
            
        Returns:
            Optional[GrammarError]: Error with adjusted positions or None if invalid
        """
        # For now, return the error as-is since preprocessing is minimal
        # In the future, this could map positions back to original text
        return error
    
    def __fallback_spell_check(self, text: str) -> List[GrammarError]:
        """
        Fallback spell check that checks individual words when full sentence check fails.
        
        Args:
            text (str): Text to check
            
        Returns:
            List[GrammarError]: List of spelling errors found
        """
        import re
        from src.services.language_analysis.models.analysis_result import GrammarError
        
        errors = []
        
        # Extract words (excluding punctuation and numbers)
        words = re.findall(r'\b[a-zA-ZäöüßÄÖÜ]+\b', text)
        
        for word in words:
            try:
                # Check each word individually
                matches = self.tool.check(word)
                for match in matches:
                    # Find the word position in the original text
                    word_start = text.find(word)
                    if word_start != -1:
                        error = GrammarError(
                            message=match.message,
                            startChar=word_start,
                            endChar=word_start + len(word),
                            suggestions=match.replacements[:5] if match.replacements else [],
                            ruleId=match.ruleId if hasattr(match, 'ruleId') else "SPELLING_RULE"
                        )
                        errors.append(error)
            except Exception as e:
                logger.debug(f"Failed to check word '{word}': {e}")
                continue
        
        return errors
    
    def __extract_error_info(self, match, text: str) -> Optional[GrammarError]:
        """
        Extract error information from a LanguageTool match.
        
        Args:
            match: LanguageTool match object
            text (str): Original text
            
        Returns:
            Optional[GrammarError]: Extracted error information or None if invalid
        """
        try:
            # Extract basic error information
            message = match.message
            start_char = match.offset
            end_char = match.offset + match.errorLength
            
            # Extract suggestions
            suggestions = []
            if match.replacements:
                suggestions = match.replacements[:5]  # Limit to 5 suggestions
            
            # Extract rule ID
            rule_id = match.ruleId if hasattr(match, 'ruleId') else "UNKNOWN_RULE"
            
            # Validate character positions
            if start_char < 0 or end_char > len(text) or start_char >= end_char:
                logger.warning(f"Invalid character positions for error: start={start_char}, end={end_char}, text_length={len(text)}")
                return None
            
            return GrammarError(
                message=message,
                startChar=start_char,
                endChar=end_char,
                suggestions=suggestions,
                ruleId=rule_id
            )
            
        except Exception as e:
            logger.error(f"Failed to extract error info from match: {e}")
            return None
    
    def check_grammar_only(self, text: str) -> List[GrammarError]:
        """
        Check text for grammar errors only (excluding spelling errors).
        
        Args:
            text (str): The text to check for grammar errors
            
        Returns:
            List[GrammarError]: List of grammar errors found
        """
        if not self.is_loaded():
            raise Exception("LanguageTool not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            # Get all matches
            all_errors = self.check_text(text)
            
            # Filter out spelling errors (typically have rule IDs containing "SPELLER" or "SPELL")
            grammar_errors = [
                error for error in all_errors 
                if not any(keyword in error.ruleId.upper() for keyword in ['SPELLER', 'SPELL', 'MORFOLOGIK'])
            ]
            
            logger.debug(f"Grammar check completed: {len(grammar_errors)} grammar errors found")
            return grammar_errors
            
        except Exception as e:
            logger.error(f"Grammar check failed: {e}")
            raise Exception(f"Grammar check failed: {e}")
    
    def check_spelling_only(self, text: str) -> List[GrammarError]:
        """
        Check text for spelling errors only (excluding grammar errors).
        
        Args:
            text (str): The text to check for spelling errors
            
        Returns:
            List[GrammarError]: List of spelling errors found
        """
        if not self.is_loaded():
            raise Exception("LanguageTool not loaded. Call load_model() first.")
        
        if not text or not text.strip():
            return []
        
        try:
            # Get all matches
            all_errors = self.check_text(text)
            
            # Filter for spelling errors (typically have rule IDs containing "SPELLER" or "SPELL")
            spelling_errors = [
                error for error in all_errors 
                if any(keyword in error.ruleId.upper() for keyword in ['SPELLER', 'SPELL', 'MORFOLOGIK'])
            ]
            
            logger.debug(f"Spelling check completed: {len(spelling_errors)} spelling errors found")
            return spelling_errors
            
        except Exception as e:
            logger.error(f"Spelling check failed: {e}")
            raise Exception(f"Spelling check failed: {e}")
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages by LanguageTool.
        
        Returns:
            List[str]: List of supported language codes in proper format (e.g., 'de-DE', 'en-US')
        """
        try:
            return language_constants.SUPPORTED_LANGUAGES.copy()
        except Exception as e:
            logger.error(f"Failed to get supported languages: {e}")
            return ['de-DE', 'en-US', 'fr-FR', 'es-ES', 'it-IT']  # Fallback to supported languages
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported by LanguageTool.
        
        Args:
            language (str): Language code to check (supports both short and long format)
            
        Returns:
            bool: True if language is supported, False otherwise
        """
        return language_constants.is_language_supported(language)
    
    def get_rule_categories(self) -> Dict[str, List[str]]:
        """
        Get available rule categories for the current language.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping categories to rule IDs
        """
        if not self.is_loaded():
            return {}
        
        try:
            # This is a simplified implementation
            # In practice, you might want to query LanguageTool's rule system
            categories = {
                'grammar': [
                    'GERMAN_CASE_AGREEMENT',
                    'GERMAN_VERB_AGREEMENT',
                    'GERMAN_PREPOSITION_CASE',
                    'GERMAN_ARTICLE_AGREEMENT'
                ],
                'spelling': [
                    'GERMAN_SPELLER_RULE',
                    'MORFOLOGIK_RULE_DE_DE'
                ],
                'style': [
                    'GERMAN_STYLE_RULE',
                    'GERMAN_WORD_ORDER'
                ]
            }
            
            return categories
            
        except Exception as e:
            logger.error(f"Failed to get rule categories: {e}")
            return {}
    
    def unload_model(self) -> None:
        """Unload LanguageTool to free memory."""
        if self.tool is not None:
            self.tool = None
            self._is_loaded = False
            logger.info(f"LanguageTool unloaded for language: {self.language}")
