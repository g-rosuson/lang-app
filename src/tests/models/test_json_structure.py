"""
Tests for JSON output structure validation.
"""

import json
from src.services.language_analysis.models.analysis_result import (
    AnalysisResult, Token, Sentence, MorphologyFeatures, 
    DependencyRelation, GrammarError
)


class TestJSONStructureValidation:
    """Test cases for JSON output structure validation."""
    
    def test_analysis_result_json_structure(self):
        """Test that AnalysisResult produces correct JSON structure."""
        # Create sample data
        morphology = MorphologyFeatures(
            Case="Nom",
            Gender="Masc",
            Number="Sing",
            additional_features={}
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
        
        sentence = Sentence(
            text="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            tokens=[token]
        )
        
        grammar_error = GrammarError(
            message="The noun 'Schüler' may require the dative case here.",
            startChar=17,
            endChar=24,
            suggestions=["dem Schüler"],
            ruleId="GERMAN_CASE_AGREEMENT"
        )
        
        analysis_result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            language="de",
            sentences=[sentence],
            errors=[grammar_error]
        )
        
        # Convert to dict
        result_dict = analysis_result.model_dump()
        
        # Validate top-level structure
        assert "originalText" in result_dict
        assert "language" in result_dict
        assert "sentences" in result_dict
        assert "errors" in result_dict
        
        # Validate originalText
        assert result_dict["originalText"] == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        
        # Validate language
        assert result_dict["language"] == "de"
        
        # Validate sentences structure
        assert isinstance(result_dict["sentences"], list)
        assert len(result_dict["sentences"]) == 1
        
        sentence_dict = result_dict["sentences"][0]
        assert "text" in sentence_dict
        assert "tokens" in sentence_dict
        assert sentence_dict["text"] == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        
        # Validate tokens structure
        assert isinstance(sentence_dict["tokens"], list)
        assert len(sentence_dict["tokens"]) == 1
        
        token_dict = sentence_dict["tokens"][0]
        required_token_fields = ["text", "startChar", "endChar", "pos", "lemma", "morphology", "dependency"]
        for field in required_token_fields:
            assert field in token_dict
        
        assert token_dict["text"] == "Der"
        assert token_dict["startChar"] == 0
        assert token_dict["endChar"] == 3
        assert token_dict["pos"] == "DET"
        assert token_dict["lemma"] == "der"
        
        # Validate morphology structure
        morphology_dict = token_dict["morphology"]
        assert isinstance(morphology_dict, dict)
        assert morphology_dict["Case"] == "Nom"
        assert morphology_dict["Gender"] == "Masc"
        assert morphology_dict["Number"] == "Sing"
        assert morphology_dict["additional_features"] == {}
        
        # Validate dependency structure
        dependency_dict = token_dict["dependency"]
        assert isinstance(dependency_dict, dict)
        assert "relation" in dependency_dict
        assert "headTokenIndex" in dependency_dict
        assert dependency_dict["relation"] == "det"
        assert dependency_dict["headTokenIndex"] == 1
        
        # Validate errors structure
        assert isinstance(result_dict["errors"], list)
        assert len(result_dict["errors"]) == 1
        
        error_dict = result_dict["errors"][0]
        required_error_fields = ["message", "startChar", "endChar", "suggestions", "ruleId"]
        for field in required_error_fields:
            assert field in error_dict
        
        assert error_dict["message"] == "The noun 'Schüler' may require the dative case here."
        assert error_dict["startChar"] == 17
        assert error_dict["endChar"] == 24
        assert error_dict["suggestions"] == ["dem Schüler"]
        assert error_dict["ruleId"] == "GERMAN_CASE_AGREEMENT"
    
    def test_json_serialization(self):
        """Test that the result can be serialized to JSON."""
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
        
        analysis_result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            language="de",
            sentences=[sentence],
            errors=[]
        )
        
        # Test JSON serialization
        result_dict = analysis_result.model_dump()
        json_str = json.dumps(result_dict, ensure_ascii=False)
        
        # Should not raise exception
        assert isinstance(json_str, str)
        assert len(json_str) > 0
        
        # Test JSON deserialization
        parsed_dict = json.loads(json_str)
        assert parsed_dict["originalText"] == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        assert parsed_dict["language"] == "de"
    
    def test_minimal_json_structure(self):
        """Test minimal JSON structure with empty data."""
        analysis_result = AnalysisResult(
            originalText="Hello World!",
            language="en",
            sentences=[],
            errors=[]
        )
        
        result_dict = analysis_result.model_dump()
        
        # Validate minimal structure
        assert result_dict["originalText"] == "Hello World!"
        assert result_dict["language"] == "en"
        assert result_dict["sentences"] == []
        assert result_dict["errors"] == []
    
    def test_multiple_sentences_structure(self):
        """Test JSON structure with multiple sentences."""
        # Create multiple sentences
        morphology1 = MorphologyFeatures(Case="Nom", Gender="Masc", Number="Sing")
        dependency1 = DependencyRelation(relation="det", headTokenIndex=1)
        
        token1 = Token(
            text="Der",
            startChar=0,
            endChar=3,
            pos="DET",
            lemma="der",
            morphology=morphology1,
            dependency=dependency1
        )
        
        sentence1 = Sentence(
            text="Der Lehrer gibt den Schüler das Buch.",
            tokens=[token1]
        )
        
        morphology2 = MorphologyFeatures(Case="Nom", Gender="Masc", Number="Sing")
        dependency2 = DependencyRelation(relation="det", headTokenIndex=1)
        
        token2 = Token(
            text="Das",
            startChar=0,
            endChar=3,
            pos="DET",
            lemma="das",
            morphology=morphology2,
            dependency=dependency2
        )
        
        sentence2 = Sentence(
            text="Das ist ein Test.",
            tokens=[token2]
        )
        
        analysis_result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Buch. Das ist ein Test.",
            language="de",
            sentences=[sentence1, sentence2],
            errors=[]
        )
        
        result_dict = analysis_result.model_dump()
        
        # Validate multiple sentences
        assert len(result_dict["sentences"]) == 2
        assert result_dict["sentences"][0]["text"] == "Der Lehrer gibt den Schüler das Buch."
        assert result_dict["sentences"][1]["text"] == "Das ist ein Test."
    
    def test_multiple_errors_structure(self):
        """Test JSON structure with multiple errors."""
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
        
        error1 = GrammarError(
            message="The noun 'Schüler' may require the dative case here.",
            startChar=17,
            endChar=24,
            suggestions=["dem Schüler"],
            ruleId="GERMAN_CASE_AGREEMENT"
        )
        
        error2 = GrammarError(
            message="Possible spelling mistake found.",
            startChar=29,
            endChar=33,
            suggestions=["Buch"],
            ruleId="GERMAN_SPELLER_RULE"
        )
        
        analysis_result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Büch des berühmten Autors.",
            language="de",
            sentences=[sentence],
            errors=[error1, error2]
        )
        
        result_dict = analysis_result.model_dump()
        
        # Validate multiple errors
        assert len(result_dict["errors"]) == 2
        assert result_dict["errors"][0]["ruleId"] == "GERMAN_CASE_AGREEMENT"
        assert result_dict["errors"][1]["ruleId"] == "GERMAN_SPELLER_RULE"
    
    def test_morphology_additional_features(self):
        """Test morphology with additional language-specific features."""
        morphology = MorphologyFeatures(
            Case="Nom",
            Gender="Masc",
            Number="Sing",
            additional_features={"Aspect": "Perf", "Definiteness": "Def"}
        )
        
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
            text="Der Lehrer gibt den Schüler das Buch.",
            tokens=[token]
        )
        
        analysis_result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Buch.",
            language="de",
            sentences=[sentence],
            errors=[]
        )
        
        result_dict = analysis_result.model_dump()
        
        # Validate additional features
        morphology_dict = result_dict["sentences"][0]["tokens"][0]["morphology"]
        assert morphology_dict["additional_features"]["Aspect"] == "Perf"
        assert morphology_dict["additional_features"]["Definiteness"] == "Def"
    
    def test_character_position_validation(self):
        """Test that character positions are correctly set."""
        morphology = MorphologyFeatures(Case="Nom", Gender="Masc", Number="Sing")
        dependency = DependencyRelation(relation="det", headTokenIndex=1)
        
        token = Token(
            text="Lehrer",
            startChar=4,
            endChar=10,
            pos="NOUN",
            lemma="Lehrer",
            morphology=morphology,
            dependency=dependency
        )
        
        sentence = Sentence(
            text="Der Lehrer gibt den Schüler das Buch.",
            tokens=[token]
        )
        
        analysis_result = AnalysisResult(
            originalText="Der Lehrer gibt den Schüler das Buch.",
            language="de",
            sentences=[sentence],
            errors=[]
        )
        
        result_dict = analysis_result.model_dump()
        
        # Validate character positions
        token_dict = result_dict["sentences"][0]["tokens"][0]
        assert token_dict["startChar"] == 4
        assert token_dict["endChar"] == 10
        assert token_dict["text"] == "Lehrer"
