"""
Pipeline Components for Adda Search Engine v5.24

Components:
- IntentAnalyzerComponent: Query -> dict med branches, search_terms
- ContextBuilderComponent: Intent -> dict med documents
- PlannerComponent: Intent + Context + Avrop -> dict med entity_changes, strategic_input
- AvropsContainerManager: Avrop + Changes -> Updated Avrop (deterministisk)
- SynthesizerComponent: Plan + Avrop -> dict med response

Pipeline:
    IntentAnalyzer → ContextBuilder → Planner → AvropsContainerManager → Synthesizer
         ↓               ↓              ↓                ↓                   ↓
       intent          context         plan         updated_avrop        response
"""
from .intent_analyzer import IntentAnalyzerComponent
from .context_builder import ContextBuilderComponent
from .planner import PlannerComponent
from .avrop_container_manager import AvropsContainerManager
from .synthesizer import SynthesizerComponent

__all__ = [
    'IntentAnalyzerComponent',
    'ContextBuilderComponent',
    'PlannerComponent',
    'AvropsContainerManager',
    'SynthesizerComponent'
]

