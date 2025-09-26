"""
Token Analysis Data Models

This module contains Pydantic models for individual token analysis results
from different NLP processors (SpaCy and Stanza).
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SpaCyToken(BaseModel):
    """SpaCy token analysis result."""
    
    text: str = Field(..., description="Original token text")
    lemma: str = Field(..., description="Lemmatized form of the token")
    pos: str = Field(..., description="Universal POS tag")
    tag: str = Field(..., description="Language-specific POS tag")
    morph: Dict[str, Any] = Field(default_factory=dict, description="Morphological features")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hallo",
                "lemma": "Hallo",
                "pos": "INTJ",
                "tag": "ITJ",
                "morph": {"Polarity": "Pos"}
            }
        }


class StanzaToken(BaseModel):
    """Stanza token analysis result."""
    
    text: str = Field(..., description="Original token text")
    lemma: str = Field(..., description="Lemmatized form of the token")
    upos: str = Field(..., description="Universal POS tag")
    xpos: str = Field(..., description="Language-specific POS tag")
    head: int = Field(..., description="Index of the head token in dependency tree")
    deprel: str = Field(..., description="Dependency relation to head token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hallo",
                "lemma": "Hallo",
                "upos": "INTJ",
                "xpos": "ITJ",
                "head": 2,
                "deprel": "discourse"
            }
        }


class TokenAnalysis(BaseModel):
    """Combined token analysis result."""
    
    text: str = Field(..., description="Original token text")
    lemma: str = Field(..., description="Lemmatized form of the token")
    pos: str = Field(..., description="Universal POS tag")
    tag: str = Field(..., description="Language-specific POS tag")
    morph: Optional[Dict[str, Any]] = Field(None, description="Morphological features (SpaCy)")
    head: Optional[int] = Field(None, description="Head token index (Stanza)")
    deprel: Optional[str] = Field(None, description="Dependency relation (Stanza)")
    processor: str = Field(..., description="Processor that generated this analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hallo",
                "lemma": "Hallo",
                "pos": "INTJ",
                "tag": "ITJ",
                "morph": {"Polarity": "Pos"},
                "head": 2,
                "deprel": "discourse",
                "processor": "spacy"
            }
        }
