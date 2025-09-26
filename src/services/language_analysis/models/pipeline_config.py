"""
Pipeline Configuration Data Models

This module contains Pydantic models for pipeline configuration and settings.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for individual NLP models."""
    
    spacy_model: str = Field(..., description="SpaCy model name")
    stanza_lang: str = Field(..., description="Stanza language code")
    stanza_processors: str = Field(..., description="Stanza processors configuration")
    spellcheck_lang: str = Field(..., description="Spell checker language")
    use_gpu: bool = Field(False, description="Whether to use GPU for processing")
    
    class Config:
        json_schema_extra = {
            "example": {
                "spacy_model": "de_core_news_md",
                "stanza_lang": "de",
                "stanza_processors": "tokenize,mwt,pos,lemma,depparse",
                "spellcheck_lang": "de",
                "use_gpu": False
            }
        }


class PipelineConfig(BaseModel):
    """Main pipeline configuration."""
    
    language: str = Field("de", description="Target language for analysis")
    enable_spellcheck: bool = Field(True, description="Enable spell checking")
    enable_spacy: bool = Field(True, description="Enable SpaCy analysis")
    enable_stanza: bool = Field(True, description="Enable Stanza analysis")
    enable_morphology: bool = Field(True, description="Enable morphological analysis")
    enable_dependency_parsing: bool = Field(True, description="Enable dependency parsing")
    max_text_length: int = Field(10000, description="Maximum text length for processing")
    timeout_seconds: int = Field(30, description="Processing timeout in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "de",
                "enable_spellcheck": True,
                "enable_spacy": True,
                "enable_stanza": True,
                "enable_morphology": True,
                "enable_dependency_parsing": True,
                "max_text_length": 10000,
                "timeout_seconds": 30
            }
        }


class ProcessingStats(BaseModel):
    """Processing statistics and performance metrics."""
    
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    spacy_time_ms: Optional[float] = Field(None, description="SpaCy processing time")
    stanza_time_ms: Optional[float] = Field(None, description="Stanza processing time")
    spellcheck_time_ms: Optional[float] = Field(None, description="Spell check processing time")
    tokens_processed: int = Field(0, description="Number of tokens processed")
    words_checked: int = Field(0, description="Number of words spell-checked")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    
    class Config:
        json_schema_extra = {
            "example": {
                "processing_time_ms": 123.45,
                "spacy_time_ms": 45.2,
                "stanza_time_ms": 67.8,
                "spellcheck_time_ms": 10.45,
                "tokens_processed": 15,
                "words_checked": 12,
                "memory_usage_mb": 256.7
            }
        }
