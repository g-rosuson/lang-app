"""
Text Preprocessing Utilities

This module provides general text preprocessing and validation utilities for
the language analysis pipeline, without language-specific assumptions.
"""

import re
from typing import Optional, Dict, Any
from ...logging.logging import get_logger

logger = get_logger(__name__)


class TextPreprocessor:
    """General text preprocessing and validation utilities."""
    
    def __init__(self, max_length: int = 10000):
        """
        Initialize the text preprocessor.
        
        Args:
            max_length (int): Maximum allowed text length
        """
        self.max_length = max_length
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess and validate input text.
        
        Args:
            text (str): The raw input text to preprocess
            
        Returns:
            str: The cleaned and validated text
            
        Raises:
            ValueError: If the text is empty or invalid
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        # Basic preprocessing: strip whitespace and normalize
        processed_text = text.strip()
        
        if not processed_text:
            raise ValueError("Text cannot be empty or only whitespace")
        
        # Check length limit
        if len(processed_text) > self.max_length:
            logger.warning(f"Text truncated from {len(processed_text)} to {self.max_length} characters")
            processed_text = processed_text[:self.max_length]
        
        logger.debug(f"Text preprocessed: '{processed_text[:50]}...'")
        return processed_text
    
    def validate_text(self, text: str) -> Dict[str, Any]:
        """
        Validate text and return validation results.
        
        Args:
            text (str): The text to validate
            
        Returns:
            Dict[str, Any]: Validation results
        """
        if not text or not text.strip():
            return {
                "valid": False,
                "reason": "empty_text",
                "message": "Text is empty or contains only whitespace"
            }
        
        # Check for basic text characteristics
        has_letters = bool(re.search(r'[a-zA-Z]', text))
        has_numbers = bool(re.search(r'\d', text))
        has_punctuation = bool(re.search(r'[^\w\s]', text))
        
        # Check for suspicious patterns
        has_repeated_chars = bool(re.search(r'(.)\1{4,}', text))  # 5+ repeated chars
        has_excessive_whitespace = bool(re.search(r'\s{10,}', text))  # 10+ spaces
        
        validation_result = {
            "valid": True,
            "has_letters": has_letters,
            "has_numbers": has_numbers,
            "has_punctuation": has_punctuation,
            "has_repeated_chars": has_repeated_chars,
            "has_excessive_whitespace": has_excessive_whitespace,
            "character_count": len(text),
            "word_count": len(text.split()),
            "warnings": []
        }
        
        # Add warnings for suspicious patterns
        if has_repeated_chars:
            validation_result["warnings"].append("Text contains repeated characters")
        if has_excessive_whitespace:
            validation_result["warnings"].append("Text contains excessive whitespace")
        if not has_letters:
            validation_result["warnings"].append("Text contains no letters")
        
        logger.debug(f"Text validation completed: {validation_result}")
        return validation_result
    
    def get_basic_stats(self, text: str) -> Dict[str, Any]:
        """
        Get basic text statistics.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            Dict[str, Any]: Basic text statistics
        """
        if not text:
            return {
                "character_count": 0,
                "word_count": 0,
                "sentence_count": 0,
                "line_count": 0,
                "paragraph_count": 0
            }
        
        # Basic counts
        character_count = len(text)
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        line_count = len(text.split('\n'))
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Character analysis
        alpha_chars = len(re.findall(r'[a-zA-Z]', text))
        digit_chars = len(re.findall(r'\d', text))
        space_chars = len(re.findall(r'\s', text))
        punctuation_chars = len(re.findall(r'[^\w\s]', text))
        
        stats = {
            "character_count": character_count,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "line_count": line_count,
            "paragraph_count": paragraph_count,
            "alpha_chars": alpha_chars,
            "digit_chars": digit_chars,
            "space_chars": space_chars,
            "punctuation_chars": punctuation_chars
        }
        
        logger.debug(f"Basic text stats: {stats}")
        return stats
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.
        
        Args:
            text (str): The text to clean
            
        Returns:
            str: The cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize quotes
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        cleaned = cleaned.replace(''', "'").replace(''', "'")
        
        # Remove excessive punctuation
        cleaned = re.sub(r'([.!?]){3,}', r'\1\1\1', cleaned)  # Max 3 punctuation marks
        
        logger.debug(f"Text cleaned: '{cleaned[:50]}...'")
        return cleaned
    
    def extract_words(self, text: str) -> list[str]:
        """
        Extract words from text for analysis.
        
        Args:
            text (str): The text to extract words from
            
        Returns:
            list[str]: List of words
        """
        if not text:
            return []
        
        # Extract words (letters, numbers, and common punctuation)
        words = re.findall(r'\b\w+\b', text)
        
        logger.debug(f"Extracted {len(words)} words from text")
        return words
    
    def detect_encoding_issues(self, text: str) -> Dict[str, Any]:
        """
        Detect potential encoding issues in text.
        
        Args:
            text (str): The text to check
            
        Returns:
            Dict[str, Any]: Encoding issue detection results
        """
        issues = {
            "has_encoding_issues": False,
            "issues": [],
            "suspicious_chars": []
        }
        
        # Check for common encoding issues
        if '\ufffd' in text:
            issues["has_encoding_issues"] = True
            issues["issues"].append("Contains replacement characters (\ufffd)")
        
        # Check for mixed encodings
        if re.search(r'[\x80-\xFF]', text):
            issues["suspicious_chars"].append("Contains high ASCII characters")
        
        # Check for control characters
        control_chars = re.findall(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', text)
        if control_chars:
            issues["has_encoding_issues"] = True
            issues["issues"].append(f"Contains {len(control_chars)} control characters")
            issues["suspicious_chars"].extend(control_chars[:5])  # Show first 5
        
        logger.debug(f"Encoding check completed: {issues}")
        return issues
