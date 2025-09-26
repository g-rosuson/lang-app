"""
Language Analysis Processors

This module contains individual processors for different NLP tools:
- SpaCy processor for tokenization, POS tagging, and morphology
- Stanza processor for advanced linguistic analysis and dependency parsing
- Spell checker processor for German spell checking and corrections
"""

from .spacy_processor import SpaCyProcessor
from .stanza_processor import StanzaProcessor
from .spell_checker import SpellCheckerProcessor

__all__ = [
    "SpaCyProcessor",
    "StanzaProcessor", 
    "SpellCheckerProcessor"
]
