"""Configuration barrel file - exports all config modules"""

from .models import DE_MD_SPACY_MODEL_NAME, DE_STANZA_LANGUAGE_NAME, STANZA_PROCESSORS

__all__ = [
    "DE_MD_SPACY_MODEL_NAME",
    "DE_STANZA_LANGUAGE_NAME",
    "STANZA_PROCESSORS",
]