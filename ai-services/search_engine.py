"""
Adda Search Engine v5
Wrapper for backwards compatibility - delegates to app.engine
"""
from app.engine import AddaSearchEngine, engine

__all__ = ['AddaSearchEngine', 'engine']
