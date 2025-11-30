"""
Pipeline Components for Adda Search Engine v5

Components:
- ExtractorComponent: Entity extraction from conversation
- IntentAnalyzerComponent: Query -> IntentTarget mapping (NEW)
- ContextBuilderComponent: Dual retrieval (replaces HunterComponent)
- PlannerComponent: Search strategy planning
- SynthesizerComponent: Response generation with persona
"""
from .extractor import ExtractorComponent
from .intent_analyzer import IntentAnalyzerComponent
from .context_builder import ContextBuilderComponent, HunterComponent  # HunterComponent is alias
from .planner import PlannerComponent
from .synthesizer import SynthesizerComponent

__all__ = [
    'ExtractorComponent',
    'IntentAnalyzerComponent',
    'ContextBuilderComponent',
    'HunterComponent',  # Alias for backward compatibility
    'PlannerComponent', 
    'SynthesizerComponent'
]

