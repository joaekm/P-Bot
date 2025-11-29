"""
Validators for Adda Search Engine v5.2
Data-driven validation using Smart Blocks from Lake.
"""
from .normalizer import normalize_entities, validate_entities, reload_from_lake

__all__ = ['normalize_entities', 'validate_entities', 'reload_from_lake']

