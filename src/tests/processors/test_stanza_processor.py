"""
Tests for StanzaProcessor.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.language_analysis.processors.stanza_processor import StanzaProcessor


class TestStanzaProcessor:
    """Test cases for StanzaProcessor."""
    
    def test_stanza_processor_initialization(self):
        """Test StanzaProcessor initialization."""
        processor = StanzaProcessor(
            language="de",
            processors="tokenize,mwt,pos,lemma,depparse",
            model_dir="/tmp/models",
            use_gpu=False
        )
        
        assert processor.language == "de"
        assert processor.processors == "tokenize,mwt,pos,lemma,depparse"
        assert processor.model_dir == "/tmp/models"
        assert processor.use_gpu is False
        assert processor.nlp is None
        assert processor._is_loaded is False
    
    def test_stanza_processor_defaults(self):
        """Test StanzaProcessor with default values."""
        processor = StanzaProcessor()
        
        assert processor.language == "de"
        assert processor.processors == "tokenize,mwt,pos,lemma,depparse"
        assert processor.model_dir is None
        assert processor.use_gpu is False
        assert processor.nlp is None
        assert processor._is_loaded is False
    
    def test_is_loaded_false_when_not_loaded(self):
        """Test is_loaded returns False when model not loaded."""
        processor = StanzaProcessor()
        
        assert processor.is_loaded() is False
    
    def test_is_loaded_true_when_loaded(self):
        """Test is_loaded returns True when model is loaded."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        assert processor.is_loaded() is True
    
    def test_is_loaded_false_when_nlp_is_none(self):
        """Test is_loaded returns False when nlp is None."""
        processor = StanzaProcessor()
        processor._is_loaded = True
        processor.nlp = None
        
        assert processor.is_loaded() is False
    
    @patch('src.services.language_analysis.processors.stanza_processor.stanza.Pipeline')
    def test_load_model_success(self, mock_pipeline):
        """Test successful model loading."""
        processor = StanzaProcessor(language="de")
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        processor.load_model()
        
        mock_pipeline.assert_called_once_with(
            lang="de",
            processors="tokenize,mwt,pos,lemma,depparse",
            use_gpu=False,
            verbose=False
        )
        assert processor.nlp == mock_pipeline_instance
        assert processor._is_loaded is True
    
    @patch('src.services.language_analysis.processors.stanza_processor.stanza.Pipeline')
    def test_load_model_with_model_dir(self, mock_pipeline):
        """Test model loading with custom model directory."""
        processor = StanzaProcessor(language="de", model_dir="/tmp/models")
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        processor.load_model()
        
        mock_pipeline.assert_called_once_with(
            lang="de",
            processors="tokenize,mwt,pos,lemma,depparse",
            use_gpu=False,
            verbose=False,
            model_dir="/tmp/models"
        )
    
    @patch('src.services.language_analysis.processors.stanza_processor.stanza.Pipeline')
    def test_load_model_failure(self, mock_pipeline):
        """Test model loading failure."""
        processor = StanzaProcessor(language="de")
        mock_pipeline.side_effect = Exception("Model loading failed")
        
        with pytest.raises(Exception, match="Could not initialize Stanza pipeline for de: Model loading failed"):
            processor.load_model()
    
    def test_analyze_comprehensive_not_loaded(self):
        """Test analyze_comprehensive raises exception when model not loaded."""
        processor = StanzaProcessor()
        
        with pytest.raises(Exception, match="Stanza model not loaded. Call load_model\\(\\) first."):
            processor.analyze_comprehensive("Test text")
    
    def test_analyze_comprehensive_empty_text(self):
        """Test analyze_comprehensive with empty text."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        result = processor.analyze_comprehensive("")
        
        assert result == []
    
    def test_analyze_comprehensive_whitespace_text(self):
        """Test analyze_comprehensive with whitespace-only text."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        result = processor.analyze_comprehensive("   \n\t   ")
        
        assert result == []
    
    @patch('src.services.language_analysis.processors.stanza_processor.time.time')
    def test_analyze_comprehensive_success(self, mock_time):
        """Test successful comprehensive analysis."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        # Mock time.time to return consistent values
        mock_time.side_effect = [0.0, 0.1]  # start_time, end_time
        
        # Mock Stanza document structure
        mock_word = Mock()
        mock_word.text = "Der"
        mock_word.lemma = "der"
        mock_word.upos = "DET"
        mock_word.xpos = "ART"
        mock_word.head = 2
        mock_word.deprel = "det"
        mock_word.id = 1
        mock_word.feats = "Case=Nom|Gender=Masc|Number=Sing"
        
        mock_sentence = Mock()
        mock_sentence.words = [mock_word]
        mock_sentence.text = "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        
        mock_doc = Mock()
        mock_doc.sentences = [mock_sentence]
        processor.nlp.return_value = mock_doc
        
        result = processor.analyze_comprehensive("Der Lehrer gibt den Schüler das Büch des berühmten Autors.")
        
        assert len(result) == 1
        assert result[0].text == "Der Lehrer gibt den Schüler das Büch des berühmten Autors."
        assert len(result[0].tokens) == 1
        assert result[0].tokens[0].text == "Der"
        assert result[0].tokens[0].startChar == 0
        assert result[0].tokens[0].endChar == 3
        assert result[0].tokens[0].pos == "DET"
        assert result[0].tokens[0].lemma == "der"
        assert result[0].tokens[0].morphology.Case == "Nom"
        assert result[0].tokens[0].morphology.Gender == "Masc"
        assert result[0].tokens[0].morphology.Number == "Sing"
        assert result[0].tokens[0].dependency.relation == "det"
        assert result[0].tokens[0].dependency.headTokenIndex == 1
    
    def test_get_sentences_not_loaded(self):
        """Test get_sentences raises exception when model not loaded."""
        processor = StanzaProcessor()
        
        with pytest.raises(Exception, match="Stanza model not loaded. Call load_model\\(\\) first."):
            processor.get_sentences("Test text")
    
    def test_get_sentences_empty_text(self):
        """Test get_sentences with empty text."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        result = processor.get_sentences("")
        
        assert result == []
    
    def test_get_sentences_success(self):
        """Test successful sentence extraction."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        mock_sentence1 = Mock()
        mock_sentence1.text = "First sentence."
        mock_sentence2 = Mock()
        mock_sentence2.text = "Second sentence."
        
        mock_doc = Mock()
        mock_doc.sentences = [mock_sentence1, mock_sentence2]
        processor.nlp.return_value = mock_doc
        
        result = processor.get_sentences("First sentence. Second sentence.")
        
        assert result == ["First sentence.", "Second sentence."]
    
    def test_get_basic_stats_not_loaded(self):
        """Test get_basic_stats raises exception when model not loaded."""
        processor = StanzaProcessor()
        
        with pytest.raises(Exception, match="Stanza model not loaded. Call load_model\\(\\) first."):
            processor.get_basic_stats("Test text")
    
    def test_get_basic_stats_empty_text(self):
        """Test get_basic_stats with empty text."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        result = processor.get_basic_stats("")
        
        expected = {
            "word_count": 0,
            "character_count": 0,
            "sentence_count": 0,
            "token_count": 0
        }
        assert result == expected
    
    def test_get_basic_stats_success(self):
        """Test successful basic stats calculation."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        mock_word1 = Mock()
        mock_word1.text = "Hello"
        mock_word2 = Mock()
        mock_word2.text = "World"
        
        mock_sentence = Mock()
        mock_sentence.words = [mock_word1, mock_word2]
        
        mock_doc = Mock()
        mock_doc.sentences = [mock_sentence]
        processor.nlp.return_value = mock_doc
        
        result = processor.get_basic_stats("Hello World")
        
        assert result["word_count"] == 2
        assert result["character_count"] == 11
        assert result["sentence_count"] == 1
        assert result["token_count"] == 2
    
    def test_unload_model(self):
        """Test model unloading."""
        processor = StanzaProcessor()
        processor.nlp = Mock()
        processor._is_loaded = True
        
        processor.unload_model()
        
        assert processor.nlp is None
        assert processor._is_loaded is False
    
    def test_unload_model_when_nlp_is_none(self):
        """Test model unloading when nlp is already None."""
        processor = StanzaProcessor()
        processor.nlp = None
        processor._is_loaded = False
        
        processor.unload_model()
        
        assert processor.nlp is None
        assert processor._is_loaded is False
