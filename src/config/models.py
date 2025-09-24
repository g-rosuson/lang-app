"""Configuration for NLP models - same models are used across all environments"""

# SpaCy models
DE_MD_SPACY_MODEL_NAME = "de_core_news_md"

# Stanza models
DE_STANZA_LANGUAGE_NAME = "de"
STANZA_PROCESSORS = "tokenize,mwt,pos,lemma,depparse"