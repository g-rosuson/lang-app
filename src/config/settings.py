"""Application settings using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List, Dict


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
    
    # NLP Model configuration
    de_md_spacy_model_name: str = "de_core_news_md"
    de_stanza_language_name: str = "de"
    stanza_processors: str = "tokenize,mwt,pos,lemma,depparse"
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "APP_",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()