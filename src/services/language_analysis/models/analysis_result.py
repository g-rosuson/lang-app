"""
Analysis Result Data Models

This module contains the main Pydantic models for complete language analysis results.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .token_analysis import TokenAnalysis
from .spellcheck_result import SpellCheckSummary
from .pipeline_config import ProcessingStats


class AnalysisResult(BaseModel):
    """Main container for complete language analysis results."""
    
    # Input information
    text: str = Field(..., description="Original input text")
    language: str = Field("de", description="Language of the analysis")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    
    # Analysis results
    spellcheck: Optional[SpellCheckSummary] = Field(None, description="Spell checking results")
    spacy_tokens: List[TokenAnalysis] = Field(default_factory=list, description="SpaCy token analysis")
    stanza_tokens: List[TokenAnalysis] = Field(default_factory=list, description="Stanza token analysis")
    
    # Basic text statistics
    word_count: int = Field(0, description="Total word count")
    character_count: int = Field(0, description="Total character count")
    sentence_count: int = Field(0, description="Total sentence count")
    
    # Processing information
    stats: Optional[ProcessingStats] = Field(None, description="Processing statistics")
    success: bool = Field(True, description="Whether analysis completed successfully")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered during processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hallo Welt! Das ist ein Test.",
                "language": "de",
                "timestamp": "2024-01-15T10:30:00Z",
                "spellcheck": {
                    "misspelled_words": {},
                    "total_misspelled": 0,
                    "total_words": 5,
                    "accuracy": 100.0
                },
                "spacy_tokens": [
                    {
                        "text": "Hallo",
                        "lemma": "Hallo",
                        "pos": "INTJ",
                        "tag": "ITJ",
                        "morph": {"Polarity": "Pos"},
                        "processor": "spacy"
                    }
                ],
                "stanza_tokens": [
                    {
                        "text": "Hallo",
                        "lemma": "Hallo",
                        "pos": "INTJ",
                        "tag": "ITJ",
                        "head": 2,
                        "deprel": "discourse",
                        "processor": "stanza"
                    }
                ],
                "word_count": 5,
                "character_count": 26,
                "sentence_count": 1,
                "stats": {
                    "processing_time_ms": 123.45,
                    "tokens_processed": 5
                },
                "success": True,
                "errors": []
            }
        }


class AnalysisRequest(BaseModel):
    """Request model for language analysis."""
    
    text: str = Field(..., description="Text to analyze", min_length=1, max_length=10000)
    language: Optional[str] = Field("de", description="Language for analysis")
    include_spellcheck: bool = Field(True, description="Include spell checking")
    include_spacy: bool = Field(True, description="Include SpaCy analysis")
    include_stanza: bool = Field(True, description="Include Stanza analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hallo Welt! Das ist ein Test.",
                "language": "de",
                "include_spellcheck": True,
                "include_spacy": True,
                "include_stanza": True
            }
        }


class AnalysisError(BaseModel):
    """Error information for failed analysis."""
    
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    processor: Optional[str] = Field(None, description="Processor that failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_type": "ModelLoadError",
                "error_message": "Failed to load SpaCy model",
                "processor": "spacy",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
