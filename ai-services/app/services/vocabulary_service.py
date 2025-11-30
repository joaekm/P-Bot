"""
Vocabulary Service - Singleton for accessing the taxonomy vocabulary at runtime.
Loads vocabulary.json and provides lookup functions for Intent Analysis.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from difflib import SequenceMatcher

logger = logging.getLogger("ADDA_ENGINE")


class VocabularyService:
    """
    Singleton service for vocabulary access.
    Loads the hierarchical vocabulary from config/vocabulary.json.
    
    Vocabulary Structure:
    {
        "taxonomy": {
            "DOMAIN_OBJECTS": {
                "ROLES": ["Projektledare", "Utvecklare", ...],
                "ARTIFACTS": ["CV", "Avtal", ...],
                ...
            },
            ...
        },
        "topics": ["Takpris", "Kompetensnivå", ...],
        "entities": ["Nivå 4", "Stockholm", ...],
        "block_types": ["RULE", "DEFINITION", ...]
    }
    """
    
    _instance: Optional["VocabularyService"] = None
    _initialized: bool = False
    
    def __new__(cls, config_path: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[Path] = None):
        # Only initialize once
        if VocabularyService._initialized:
            return
            
        # Default path: ai-services/config/vocabulary.json
        if config_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            config_path = base_dir / "config" / "vocabulary.json"
        
        self.config_path = config_path
        self.vocabulary: Dict = {}
        self.topics: Set[str] = set()
        self.entities: Set[str] = set()
        self.taxonomy: Dict[str, Dict[str, List[str]]] = {}
        
        self._load_vocabulary()
        VocabularyService._initialized = True
    
    def _load_vocabulary(self):
        """Load vocabulary from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"Vocabulary file not found: {self.config_path}")
            # Initialize with empty defaults
            self.vocabulary = {"taxonomy": {}, "topics": [], "entities": []}
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.vocabulary = json.load(f)
            
            # Extract sets for fast lookup
            self.topics = set(self.vocabulary.get("topics", []))
            self.entities = set(self.vocabulary.get("entities", []))
            self.taxonomy = self.vocabulary.get("taxonomy", {})
            
            logger.info(f"Vocabulary loaded: {len(self.topics)} topics, {len(self.entities)} entities")
            
        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")
            self.vocabulary = {"taxonomy": {}, "topics": [], "entities": []}
    
    def reload(self):
        """Force reload of vocabulary (useful after re-indexing)."""
        VocabularyService._initialized = False
        self._load_vocabulary()
        VocabularyService._initialized = True
    
    # =========================================================================
    # LOOKUP FUNCTIONS
    # =========================================================================
    
    def get_taxonomy_structure(self) -> Dict[str, Dict[str, List[str]]]:
        """Get the full taxonomy hierarchy."""
        return self.taxonomy
    
    def get_known_topics(self) -> List[str]:
        """Get all known topics as a list."""
        return list(self.topics)
    
    def get_known_entities(self) -> List[str]:
        """Get all known entities as a list."""
        return list(self.entities)
    
    def get_branches_for_root(self, root: str) -> List[str]:
        """Get all branches under a taxonomy root."""
        return list(self.taxonomy.get(root, {}).keys())
    
    def get_topics_for_branch(self, root: str, branch: str) -> List[str]:
        """Get topics under a specific branch."""
        return self.taxonomy.get(root, {}).get(branch, [])
    
    # =========================================================================
    # SEARCH FUNCTIONS
    # =========================================================================
    
    def search_topics(self, query: str, threshold: float = 0.6) -> List[str]:
        """
        Fuzzy search for topics matching the query.
        Returns topics with similarity >= threshold.
        """
        query_lower = query.lower()
        matches = []
        
        for topic in self.topics:
            topic_lower = topic.lower()
            
            # Exact substring match
            if query_lower in topic_lower or topic_lower in query_lower:
                matches.append((topic, 1.0))
                continue
            
            # Fuzzy match
            ratio = SequenceMatcher(None, query_lower, topic_lower).ratio()
            if ratio >= threshold:
                matches.append((topic, ratio))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches]
    
    def search_entities(self, query: str, threshold: float = 0.6) -> List[str]:
        """
        Fuzzy search for entities matching the query.
        Returns entities with similarity >= threshold.
        """
        query_lower = query.lower()
        matches = []
        
        for entity in self.entities:
            entity_lower = entity.lower()
            
            # Exact substring match
            if query_lower in entity_lower or entity_lower in query_lower:
                matches.append((entity, 1.0))
                continue
            
            # Fuzzy match
            ratio = SequenceMatcher(None, query_lower, entity_lower).ratio()
            if ratio >= threshold:
                matches.append((entity, ratio))
        
        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches]
    
    def find_branch_for_topic(self, topic: str) -> Optional[tuple]:
        """
        Find which root/branch a topic belongs to.
        Returns (root, branch) or None if not found.
        """
        topic_lower = topic.lower()
        
        for root, branches in self.taxonomy.items():
            for branch, topics in branches.items():
                for t in topics:
                    if t.lower() == topic_lower:
                        return (root, branch)
        
        return None
    
    def extract_known_concepts(self, text: str) -> Dict[str, List[str]]:
        """
        Extract known topics and entities from a text string.
        Used by IntentAnalyzer to map query to taxonomy.
        
        Returns:
            {
                "topics": ["Takpris", ...],
                "entities": ["Nivå 4", ...],
                "branches": ["FINANCIALS", ...]
            }
        """
        text_lower = text.lower()
        found_topics = []
        found_entities = []
        found_branches = set()
        
        # Find topics
        for topic in self.topics:
            if topic.lower() in text_lower:
                found_topics.append(topic)
                # Also track which branch this topic belongs to
                location = self.find_branch_for_topic(topic)
                if location:
                    found_branches.add(location[1])
        
        # Find entities
        for entity in self.entities:
            if entity.lower() in text_lower:
                found_entities.append(entity)
        
        return {
            "topics": found_topics,
            "entities": found_entities,
            "branches": list(found_branches)
        }
    
    def get_prompt_context(self) -> str:
        """
        Generate a context string for LLM prompts.
        Lists known topics and entities for better classification.
        """
        topics_sample = list(self.topics)[:50]  # Limit for prompt size
        entities_sample = list(self.entities)[:30]
        
        return f"""
KÄNDA BEGREPP (topics): {', '.join(topics_sample)}
KÄNDA ENTITETER (entities): {', '.join(entities_sample)}
"""


# Convenience function to get singleton instance
def get_vocabulary_service(config_path: Optional[Path] = None) -> VocabularyService:
    """Get or create the VocabularyService singleton."""
    return VocabularyService(config_path)

