"""
Tests for language analysis data models.
"""

from datetime import datetime
from src.services.language_analysis.models import (
    AnalysisResult, AnalysisRequest, TokenAnalysis, 
    SpaCyToken, StanzaToken, SpellCheckResult, SpellCheckSummary
)


class TestAnalysisRequest:
    """Test cases for AnalysisRequest model."""
    
    def test_analysis_request_creation(self):
        """Test creating an AnalysisRequest."""
        request = AnalysisRequest(
            text="Hello World!",
            language="de",
            include_spellcheck=True,
            include_spacy=True,
            include_stanza=True
        )
        
        assert request.text == "Hello World!"
        assert request.language == "de"
        assert request.include_spellcheck is True
        assert request.include_spacy is True
        assert request.include_stanza is True
    
    def test_analysis_request_defaults(self):
        """Test AnalysisRequest with default values."""
        request = AnalysisRequest(text="Hello World!")
        
        assert request.text == "Hello World!"
        assert request.language == "de"
        assert request.include_spellcheck is True
        assert request.include_spacy is True
        assert request.include_stanza is True


class TestTokenAnalysis:
    """Test cases for TokenAnalysis model."""
    
    def test_token_analysis_creation(self):
        """Test creating a TokenAnalysis."""
        token = TokenAnalysis(
            text="Hallo",
            lemma="Hallo",
            pos="INTJ",
            tag="ITJ",
            morph={"Polarity": "Pos"},
            head=2,
            deprel="discourse",
            processor="spacy"
        )
        
        assert token.text == "Hallo"
        assert token.lemma == "Hallo"
        assert token.pos == "INTJ"
        assert token.tag == "ITJ"
        assert token.morph == {"Polarity": "Pos"}
        assert token.head == 2
        assert token.deprel == "discourse"
        assert token.processor == "spacy"


class TestSpaCyToken:
    """Test cases for SpaCyToken model."""
    
    def test_spacy_token_creation(self):
        """Test creating a SpaCyToken."""
        token = SpaCyToken(
            text="Hallo",
            lemma="Hallo",
            pos="INTJ",
            tag="ITJ",
            morph={"Polarity": "Pos"}
        )
        
        assert token.text == "Hallo"
        assert token.lemma == "Hallo"
        assert token.pos == "INTJ"
        assert token.tag == "ITJ"
        assert token.morph == {"Polarity": "Pos"}


class TestStanzaToken:
    """Test cases for StanzaToken model."""
    
    def test_stanza_token_creation(self):
        """Test creating a StanzaToken."""
        token = StanzaToken(
            text="Hallo",
            lemma="Hallo",
            upos="INTJ",
            xpos="ITJ",
            head=2,
            deprel="discourse"
        )
        
        assert token.text == "Hallo"
        assert token.lemma == "Hallo"
        assert token.upos == "INTJ"
        assert token.xpos == "ITJ"
        assert token.head == 2
        assert token.deprel == "discourse"


class TestSpellCheckResult:
    """Test cases for SpellCheckResult model."""
    
    def test_spell_check_result_creation(self):
        """Test creating a SpellCheckResult."""
        result = SpellCheckResult(
            word="Wrld",
            candidates=["Welt", "Wald"],
            confidence=0.85
        )
        
        assert result.word == "Wrld"
        assert result.candidates == ["Welt", "Wald"]
        assert result.confidence == 0.85


class TestSpellCheckSummary:
    """Test cases for SpellCheckSummary model."""
    
    def test_spell_check_summary_creation(self):
        """Test creating a SpellCheckSummary."""
        summary = SpellCheckSummary(
            misspelled_words={"Wrld": ["Welt"]},
            total_misspelled=1,
            total_words=5,
            accuracy=80.0
        )
        
        assert summary.misspelled_words == {"Wrld": ["Welt"]}
        assert summary.total_misspelled == 1
        assert summary.total_words == 5
        assert summary.accuracy == 80.0


class TestAnalysisResult:
    """Test cases for AnalysisResult model."""
    
    def test_analysis_result_creation(self):
        """Test creating an AnalysisResult."""
        result = AnalysisResult(
            text="Hallo Welt!",
            language="de",
            word_count=2,
            character_count=11,
            sentence_count=1,
            success=True,
            errors=[]
        )
        
        assert result.text == "Hallo Welt!"
        assert result.language == "de"
        assert result.word_count == 2
        assert result.character_count == 11
        assert result.sentence_count == 1
        assert result.success is True
        assert result.errors == []
        assert isinstance(result.timestamp, datetime)
    
    def test_analysis_result_defaults(self):
        """Test AnalysisResult with default values."""
        result = AnalysisResult(text="Hello World!")
        
        assert result.text == "Hello World!"
        assert result.language == "de"
        assert result.word_count == 0
        assert result.character_count == 0
        assert result.sentence_count == 0
        assert result.success is True
        assert result.errors == []
        assert isinstance(result.timestamp, datetime)
