"""
Language constants and mappings for LanguageTool integration.

This module provides centralized language code mappings and constants
to ensure consistency across the language analysis pipeline.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class LanguageInfo(BaseModel):
    """Information about a supported language."""
    
    code: str = Field(..., description="Language code in proper format (e.g., 'de-DE')")
    name: str = Field(..., description="Human-readable language name")
    short_code: str = Field(..., description="Short language code (e.g., 'de')")


class LanguageConstants(BaseModel):
    """Centralized language constants and mappings."""
    
    # Mapping from short codes to proper LanguageTool format
    SHORT_TO_LONG_CODE: Dict[str, str] = Field(
        default_factory=lambda: {
            'de': 'de-DE',  # German (Germany)
            'en': 'en-US',  # English (US)
            'fr': 'fr-FR',  # French (France)
            'es': 'es-ES',  # Spanish (Spain)
            'it': 'it-IT',  # Italian (Italy)
        },
        description="Mapping from short language codes to proper LanguageTool format"
    )
    
    # Supported languages with proper format codes
    SUPPORTED_LANGUAGES: List[str] = Field(
        default_factory=lambda: [
            'de-DE', 'en-US', 'fr-FR', 'es-ES', 'it-IT'
        ],
        description="List of supported languages in proper LanguageTool format"
    )
    
    # Language information for display purposes
    LANGUAGE_INFO: List[LanguageInfo] = Field(
        default_factory=lambda: [
            LanguageInfo(code='de-DE', name='German (Germany)', short_code='de'),
            LanguageInfo(code='en-US', name='English (US)', short_code='en'),
            LanguageInfo(code='fr-FR', name='French (France)', short_code='fr'),
            LanguageInfo(code='es-ES', name='Spanish (Spain)', short_code='es'),
            LanguageInfo(code='it-IT', name='Italian (Italy)', short_code='it'),
        ],
        description="Detailed language information for display and validation"
    )
    
    def normalize_language_code(self, language: str) -> str:
        """
        Convert short language codes to proper LanguageTool format.
        
        Args:
            language (str): Language code (e.g., 'de', 'en', 'de-DE')
            
        Returns:
            str: Normalized language code for LanguageTool (e.g., 'de-DE', 'en-US')
        """
        # If already in proper format (contains '-'), return as-is
        if '-' in language:
            return language
        
        # Return mapped language or fallback to original if not found
        return self.SHORT_TO_LONG_CODE.get(language.lower(), language)
    
    def is_language_supported(self, language: str) -> bool:
        """
        Check if a language is supported by LanguageTool.
        
        Args:
            language (str): Language code to check (supports both short and long format)
            
        Returns:
            bool: True if language is supported, False otherwise
        """
        # Normalize the language code to check against supported languages
        normalized_language = self.normalize_language_code(language)
        return normalized_language in self.SUPPORTED_LANGUAGES
    
    def get_language_info(self, language: str) -> Optional[LanguageInfo]:
        """
        Get detailed language information for a given language code.
        
        Args:
            language (str): Language code (supports both short and long format)
            
        Returns:
            Optional[LanguageInfo]: Language information or None if not found
        """
        normalized_language = self.normalize_language_code(language)
        
        for info in self.LANGUAGE_INFO:
            if info.code == normalized_language:
                return info
        
        return None
    
    def get_supported_languages_for_display(self) -> List[Dict[str, str]]:
        """
        Get supported languages in format suitable for API responses.
        
        Returns:
            List[Dict[str, str]]: List of language dictionaries with code and name
        """
        return [
            {"code": info.code, "name": info.name}
            for info in self.LANGUAGE_INFO
        ]


# Global instance for easy access
language_constants = LanguageConstants()
