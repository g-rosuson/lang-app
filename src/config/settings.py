"""Application settings using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # App metadata (currently used in main.py)
    app_name: str = "Language App"
    app_version: str = "1.0.0"
    
    # API configuration (currently used in main.py)
    api_v1_prefix: str = "/api/v1"
    
    # Health check settings (currently used in health.py)
    health_status: str = "healthy"
    
    # Supported languages (currently used in language.py)
    supported_languages: List[Dict[str, str]] = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"}
    ]
    
    # Language Analysis Pipeline Configuration
    language_analysis_enabled: bool = True
    max_text_length: int = 10000
    default_language: str = "de"
    
    # SpaCy Configuration
    spacy_model: str = "de_core_news_md"
    
    # Stanza Configuration
    stanza_language: str = "de"
    stanza_processors: str = "tokenize,mwt,pos,lemma,depparse"
    stanza_model_dir: Optional[str] = None
    use_gpu: bool = False
    
    # Spell Checker Configuration
    spellcheck_language: str = "de"
    
    # Performance Configuration
    pipeline_timeout_seconds: int = 30
    enable_parallel_processing: bool = False
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "APP_",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()