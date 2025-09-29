"""
Tests for comprehensive language analysis data models.
"""

from src.services.language_analysis.models import (
    AnalysisResult, AnalysisRequest, Token, Sentence, 
    MorphologyFeatures, DependencyRelation, GrammarError
)


class TestMorphologyFeatures:
    """Test cases for MorphologyFeatures model."""
    
    def test_morphology_features_creation(self):
        """Test creating MorphologyFeatures."""
        morphology = MorphologyFeatures(
            Case="Nom",
            Gender="Masc",
            Number="Sing",
            Tense="Pres",
            Person="3",
            Mood="Ind",
            Voice="Act",
            Degree="Pos",
            additional_features={"Aspect": "Perf"}
        )
        
        assert morphology.Case == "Nom"
        assert morphology.Gender == "Masc"
        assert morphology.Number == "Sing"
        assert morphology.Tense == "Pres"
        assert morphology.Person == "3"
        assert morphology.Mood == "Ind"
        assert morphology.Voice == "Act"
        assert morphology.Degree == "Pos"
        assert morphology.additional_features == {"Aspect": "Perf"}
    
    def test_morphology_features_minimal(self):
        """Test creating MorphologyFeatures with minimal data."""
        morphology = MorphologyFeatures()
        
        assert morphology.Case is None
        assert morphology.Gender is None
        assert morphology.Number is None
        assert morphology.additional_features == {}


class TestDependencyRelation:
    """Test cases for DependencyRelation model."""
    
    def test_dependency_relation_creation(self):
        """Test creating DependencyRelation."""
        dependency = DependencyRelation(
            relation="det",
            headTokenIndex=1
        )
        
        assert dependency.relation == "det"
        assert dependency.headTokenIndex == 1


class TestToken:
    """Test cases for Token model."""
    
    def test_token_creation(self):
        """Test creating a Token."""
        morphology = MorphologyFeatures(
            Case="Nom",
            Gender="Masc",
            Number="Sing"
        )
        dependency = DependencyRelation(
            relation="det",
            headTokenIndex=1
        )
        
        token = Token(
            text="Der",
            startChar=0,
            endChar=3,
            pos="DET",
            lemma="der",
            morphology=morphology,
            dependency=dependency
        )
        
        assert token.text == "Der"
        assert token.startChar == 0
        assert token.endChar == 3
        assert token.pos == "DET"
        assert token.lemma == "der"
        assert token.morphology.Case == "Nom"
        assert token.morphology.Gender == "Masc"
        assert token.morphology.Number == "Sing"
        assert token.dependency.relation == "det"
        assert token.dependency.headTokenIndex == 1


class TestSentence:
    """Test cases for Sentence model."""
    
    def test_sentence_creation(self):
        """Test creating a Sentence."""
        morphology = MorphologyFeatures(Case="Nom", Gender="Masc", Number="Sing")
        dependency = DependencyRelation(relation="det", headTokenIndex=1)
        
        token = Token(
            text="Der",
            startChar=0,
            endChar=3,
            pos="DET",
            lemma="der",
            morphology=morphology,
            dependency=dependency
        )
        
        sentence = Sentence(
            text="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            tokens=[token]
        )
        
        assert sentence.text == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        assert len(sentence.tokens) == 1
        assert sentence.tokens[0].text == "Der"


class TestGrammarError:
    """Test cases for GrammarError model."""
    
    def test_grammar_error_creation(self):
        """Test creating a GrammarError."""
        error = GrammarError(
            message="The noun 'Schüler' may require the dative case here.",
            startChar=17,
            endChar=24,
            suggestions=["dem Schüler"],
            ruleId="GERMAN_CASE_AGREEMENT"
        )
        
        assert error.message == "The noun 'Schüler' may require the dative case here."
        assert error.startChar == 17
        assert error.endChar == 24
        assert error.suggestions == ["dem Schüler"]
        assert error.ruleId == "GERMAN_CASE_AGREEMENT"


class TestAnalysisRequest:
    """Test cases for AnalysisRequest model."""
    
    def test_analysis_request_creation(self):
        """Test creating an AnalysisRequest."""
        request = AnalysisRequest(
            text="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            language="de",
            include_grammar_check=True,
            include_morphological_analysis=True,
            include_dependency_parsing=True
        )
        
        assert request.text == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        assert request.language == "de"
        assert request.include_grammar_check is True
        assert request.include_morphological_analysis is True
        assert request.include_dependency_parsing is True
    
    def test_analysis_request_defaults(self):
        """Test AnalysisRequest with default values."""
        request = AnalysisRequest(text="Hello World!", language="de")
        
        assert request.text == "Hello World!"
        assert request.language == "de"
        assert request.include_grammar_check is True
        assert request.include_morphological_analysis is True
        assert request.include_dependency_parsing is True


class TestAnalysisResult:
    """Test cases for AnalysisResult model."""
    
    def test_analysis_result_creation(self):
        """Test creating an AnalysisResult."""
        morphology = MorphologyFeatures(Case="Nom", Gender="Masc", Number="Sing")
        dependency = DependencyRelation(relation="det", headTokenIndex=1)
        
        token = Token(
            text="Der",
            startChar=0,
            endChar=3,
            pos="DET",
            lemma="der",
            morphology=morphology,
            dependency=dependency
        )
        
        sentence = Sentence(
            text="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            tokens=[token]
        )
        
        error = GrammarError(
            message="The noun 'Schüler' may require the dative case here.",
            startChar=17,
            endChar=24,
            suggestions=["dem Schüler"],
            ruleId="GERMAN_CASE_AGREEMENT"
        )
        
        result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            language="de",
            sentences=[sentence],
            errors=[error]
        )
        
        assert result.originalText == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        assert result.language == "de"
        assert len(result.sentences) == 1
        assert len(result.sentences[0].tokens) == 1
        assert len(result.errors) == 1
        assert result.errors[0].ruleId == "GERMAN_CASE_AGREEMENT"
    
    def test_analysis_result_minimal(self):
        """Test AnalysisResult with minimal data."""
        result = AnalysisResult(
            originalText="Hello World!",
            language="en",
            sentences=[],
            errors=[]
        )
        
        assert result.originalText == "Hello World!"
        assert result.language == "en"
        assert result.sentences == []
        assert result.errors == []
    
    def test_analysis_result_json_serialization(self):
        """Test that AnalysisResult can be serialized to JSON."""
        morphology = MorphologyFeatures(Case="Nom", Gender="Masc", Number="Sing")
        dependency = DependencyRelation(relation="det", headTokenIndex=1)
        
        token = Token(
            text="Der",
            startChar=0,
            endChar=3,
            pos="DET",
            lemma="der",
            morphology=morphology,
            dependency=dependency
        )
        
        sentence = Sentence(
            text="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            tokens=[token]
        )
        
        result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            language="de",
            sentences=[sentence],
            errors=[]
        )
        
        # Test that model_dump() works
        result_dict = result.model_dump()
        
        assert "originalText" in result_dict
        assert "language" in result_dict
        assert "sentences" in result_dict
        assert "errors" in result_dict
        assert result_dict["originalText"] == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        assert result_dict["language"] == "de"
        assert len(result_dict["sentences"]) == 1
        assert len(result_dict["errors"]) == 0