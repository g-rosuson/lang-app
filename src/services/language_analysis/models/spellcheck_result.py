"""
Spell Check Result Data Models

This module contains Pydantic models for spell checking results and suggestions.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SpellCheckResult(BaseModel):
    """Spell checking result for a single word."""
    
    word: str = Field(..., description="The misspelled word")
    candidates: List[str] = Field(..., description="List of correction candidates")
    confidence: Optional[float] = Field(None, description="Confidence score for the correction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "Wrld",
                "candidates": ["Welt", "Wald", "Ward"],
                "confidence": 0.85
            }
        }


class SpellCheckSummary(BaseModel):
    """Summary of spell checking results for the entire text."""
    
    misspelled_words: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Dictionary mapping misspelled words to their correction candidates"
    )
    total_misspelled: int = Field(0, description="Total number of misspelled words found")
    total_words: int = Field(0, description="Total number of words checked")
    accuracy: float = Field(0.0, description="Spelling accuracy percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "misspelled_words": {
                    "Wrld": ["Welt"],
                    "Tst": ["Test", "Tast"]
                },
                "total_misspelled": 2,
                "total_words": 5,
                "accuracy": 60.0
            }
        }
