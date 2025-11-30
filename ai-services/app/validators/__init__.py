"""
Validators for Adda Search Engine v5.3

NOTE: In v5.3, normalizer.py was removed.
- Entity normalization is now in IntentAnalyzer._normalize_entities()
- Constraint validation is now in Planner._validate_against_rules()

This package is kept for backward compatibility but is now empty.
"""

# Legacy exports removed in v5.3:
# - normalize_entities -> IntentAnalyzer
# - validate_entities -> Planner
# - reload_from_lake -> No longer needed (Planner loads on demand)

__all__ = []
