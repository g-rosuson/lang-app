"""Application settings using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional

from ..services.language_analysis.models.language_constants import language_constants


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
    @property
    def supported_languages(self) -> List[Dict[str, str]]:
        """Get supported languages from centralized constants."""
        return language_constants.get_supported_languages_for_display()
    
    # Language Analysis Pipeline Configuration
    language_analysis_enabled: bool = True
    max_text_length: int = 10000
    default_language: str = "de-DE"
    
    # Stanza Configuration
    stanza_language: str = "de"
    stanza_processors: str = "tokenize,mwt,pos,lemma,depparse"
    stanza_model_dir: Optional[str] = None
    use_gpu: bool = False
    
    # LanguageTool Configuration
    language_tool_language: str = "de-DE"
    
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