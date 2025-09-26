"""
Language Analysis Service

This module provides comprehensive German language analysis capabilities including:
- Tokenization, POS tagging, and lemmatization (SpaCy)
- Advanced linguistic analysis and dependency parsing (Stanza)
- Spell checking and correction suggestions (PySpellChecker)

The service follows a modular architecture with individual processors for each
NLP tool, allowing for flexible and maintainable text analysis.
"""

from .pipeline import LanguageAnalysisPipeline, get_language_analysis_service, initialize_pipeline

__all__ = [
    "LanguageAnalysisPipeline",
    "get_language_analysis_service",
    "initialize_pipeline"
]
