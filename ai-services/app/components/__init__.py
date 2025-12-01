"""
Pipeline Components for Adda Search Engine v5.5

Components:
- IntentAnalyzerComponent: Query -> IntentTarget with search strategy (LLM-driven)
- ContextBuilderComponent: Dual retrieval (keyword + vector + graph)
- PlannerComponent: Logic layer (reasoning + validation)
- SynthesizerComponent: Response generation + Entity extraction

v5.5 Changes:
- IntentAnalyzer is now LLM-driven (no hardcoded patterns)
- Entity extraction moved to Synthesizer (context-aware)
- Synthesizer returns SynthesizerResult with response + avrop_changes
- DELETE support in Synthesizer ("ta bort X", "vi behöver inte X")
"""
from .intent_analyzer import IntentAnalyzerComponent
from .context_builder import ContextBuilderComponent
from .planner import PlannerComponent
from .synthesizer import SynthesizerComponent

__all__ = [
    'IntentAnalyzerComponent',
    'ContextBuilderComponent',
    'PlannerComponent', 
    'SynthesizerComponent'
]

