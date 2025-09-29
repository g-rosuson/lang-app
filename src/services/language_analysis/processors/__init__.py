"""
Language Analysis Processors

This module contains individual processors for different NLP tools:
- Stanza processor for comprehensive linguistic analysis with character positions, morphology, and dependency parsing
- LanguageTool processor for grammar and spell checking with error extraction
"""

from .stanza_processor import StanzaProcessor
from .language_tool_processor import LanguageToolProcessor

__all__ = [
    "StanzaProcessor", 
    "LanguageToolProcessor"
]
