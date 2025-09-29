"""
Analysis Result Data Models

This module contains Pydantic models for comprehensive language analysis results
from Stanza (tokenization, POS tagging, lemmatization, morphological analysis, dependency parsing)
and LanguageTool (grammar and spell checking) that support multiple languages.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class MorphologyFeatures(BaseModel):
    """Morphological features extracted from Stanza analysis.
    
    Features vary by language but commonly include:
    - Case: Grammatical case (Nom, Acc, Dat, Gen, etc.)
    - Gender: Grammatical gender (Masc, Fem, Neut, etc.)
    - Number: Grammatical number (Sing, Plur, etc.)
    - Tense: Verb tense (Pres, Past, Fut, etc.)
    - Person: Person (1, 2, 3)
    - Mood: Verb mood (Ind, Sub, Imp, etc.)
    - Voice: Verb voice (Act, Pass, etc.)
    - Degree: Adjective degree (Pos, Comp, Sup, etc.)
    """
    
    # Common morphological features across languages
    Case: Optional[str] = Field(None, description="Grammatical case")
    Gender: Optional[str] = Field(None, description="Grammatical gender")
    Number: Optional[str] = Field(None, description="Grammatical number")
    Tense: Optional[str] = Field(None, description="Verb tense")
    Person: Optional[str] = Field(None, description="Person")
    Mood: Optional[str] = Field(None, description="Verb mood")
    Voice: Optional[str] = Field(None, description="Verb voice")
    Degree: Optional[str] = Field(None, description="Adjective degree")
    
    # Additional language-specific features
    additional_features: Dict[str, str] = Field(default_factory=dict, description="Language-specific morphological features")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Case": "Nom",
                "Gender": "Masc", 
                "Number": "Sing",
                "additional_features": {}
            }
        }
    )


class DependencyRelation(BaseModel):
    """Dependency relation information for a token."""
    
    relation: str = Field(..., description="Dependency relation type (e.g., 'det', 'nsubj', 'obj')")
    headTokenIndex: int = Field(..., description="Index of the head token in the sentence")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "relation": "det",
                "headTokenIndex": 1
            }
        }
    )


class Token(BaseModel):
    """Token analysis with character positions, POS, lemma, morphology, and dependency info."""
    
    text: str = Field(..., description="Original token text")
    startChar: int = Field(..., description="Start character position in the original text")
    endChar: int = Field(..., description="End character position in the original text")
    pos: str = Field(..., description="Universal POS tag (e.g., 'DET', 'NOUN', 'VERB')")
    lemma: str = Field(..., description="Lemmatized form of the token")
    morphology: MorphologyFeatures = Field(..., description="Detailed morphological features")
    dependency: DependencyRelation = Field(..., description="Dependency relation information")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "Der",
                "startChar": 0,
                "endChar": 3,
                "pos": "DET",
                "lemma": "der",
                "morphology": {
                    "Case": "Nom",
                    "Gender": "Masc",
                    "Number": "Sing",
                    "additional_features": {}
                },
                "dependency": {
                    "relation": "det",
                    "headTokenIndex": 1
                }
            }
        }
    )


class Sentence(BaseModel):
    """Analysis results for a single sentence."""
    
    text: str = Field(..., description="Original sentence text")
    tokens: List[Token] = Field(..., description="List of token analyses")
    
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "text": "Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
                "tokens": [
                    {
                        "text": "Der",
                        "startChar": 0,
                        "endChar": 3,
                        "pos": "DET",
                        "lemma": "der",
                        "morphology": {
                            "Case": "Nom",
                            "Gender": "Masc",
                            "Number": "Sing",
                            "additional_features": {}
                        },
                        "dependency": {
                            "relation": "det",
                            "headTokenIndex": 1
                        }
                    }
                ]
            }
        }
    )


class GrammarError(BaseModel):
    """Grammar or spell checking error found by LanguageTool."""
    
    message: str = Field(..., description="User-friendly error message")
    startChar: int = Field(..., description="Start character position of the error")
    endChar: int = Field(..., description="End character position of the error")
    suggestions: List[str] = Field(..., description="List of correction suggestions")
    ruleId: str = Field(..., description="Internal rule ID for the error type")
    
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "message": "The noun 'Schüler' may require the dative case here.",
                "startChar": 17,
                "endChar": 24,
                "suggestions": ["dem Schüler"],
                "ruleId": "GERMAN_CASE_AGREEMENT"
            }
        }
    )


class AnalysisResult(BaseModel):
    """Complete analysis result from Stanza and LanguageTool matching the required JSON structure.
    
    This model supports multiple languages and provides comprehensive linguistic analysis including:
    - Tokenization with character positions
    - Part-of-Speech tagging
    - Lemmatization
    - Morphological analysis
    - Dependency parsing
    - Grammar and spell checking
    """
    
    originalText: str = Field(..., description="Original input text")
    language: str = Field(..., description="Language code (e.g., 'de', 'en', 'fr', 'es')")
    sentences: List[Sentence] = Field(..., description="List of sentence analyses")
    errors: List[GrammarError] = Field(default_factory=list, description="List of grammar/spelling errors")
    
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "originalText": "Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
                "language": "de",
                "sentences": [
                    {
                        "text": "Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
                        "tokens": [
                            {
                                "text": "Der",
                                "startChar": 0,
                                "endChar": 3,
                                "pos": "DET",
                                "lemma": "der",
                                "morphology": {
                                    "Case": "Nom",
                                    "Gender": "Masc",
                                    "Number": "Sing",
                                    "additional_features": {}
                                },
                                "dependency": {
                                    "relation": "det",
                                    "headTokenIndex": 1
                                }
                            }
                        ]
                    }
                ],
                "errors": [
                    {
                        "message": "The noun 'Schüler' may require the dative case here.",
                        "startChar": 17,
                        "endChar": 24,
                        "suggestions": ["dem Schüler"],
                        "ruleId": "GERMAN_CASE_AGREEMENT"
                    },
                    {
                        "message": "Possible spelling mistake found.",
                        "startChar": 29,
                        "endChar": 33,
                        "suggestions": ["Buch"],
                        "ruleId": "GERMAN_SPELLER_RULE"
                    }
                ]
            }
        }
    )


class AnalysisRequest(BaseModel):
    """Request model for language analysis."""
    
    text: str = Field(..., description="Text to analyze", min_length=1, max_length=10000)
    language: str = Field(..., description="Language code for analysis (e.g., 'de', 'en', 'fr', 'es')")
    include_grammar_check: bool = Field(True, description="Include grammar and spell checking")
    include_morphological_analysis: bool = Field(True, description="Include detailed morphological analysis")
    include_dependency_parsing: bool = Field(True, description="Include dependency parsing")
    
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "text": "Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
                "language": "de",
                "include_grammar_check": True,
                "include_morphological_analysis": True,
                "include_dependency_parsing": True
            }
        }
    )


class AnalysisError(BaseModel):
    """Error information for failed analysis."""
    
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    processor: Optional[str] = Field(None, description="Processor that failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "error_type": "ModelLoadError",
                "error_message": "Failed to load Stanza model for language 'de'",
                "processor": "stanza",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )