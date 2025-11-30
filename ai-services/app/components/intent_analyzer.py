"""
Intent Analyzer Component - Query to Taxonomy Mapping
Maps user queries to IntentTarget with taxonomy coordinates.
Uses VocabularyService for concept matching.

All keywords and prompts are loaded from config/assistant_prompts.yaml
"""
import json
import logging
import re
from typing import List, Dict, Optional

from google.genai import types

from ..models import (
    IntentTarget,
    TaxonomyRoot,
    TaxonomyBranch,
    ScopeContext,
    VALID_BRANCHES,
)
from ..services import VocabularyService

logger = logging.getLogger("ADDA_ENGINE")


class IntentAnalyzerComponent:
    """
    Intent Analyzer - Maps user queries to taxonomy coordinates.
    
    Pipeline:
    1. Extract known topics/entities using VocabularyService
    2. Classify intent (FACT/INSPIRATION/INSTRUCTION) using keywords from config
    3. Detect taxonomy branches using patterns from config
    4. Infer additional branches from detected topics (Topic-to-Branch Inference)
    5. Return IntentTarget for ContextBuilder
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
        self.vocabulary = VocabularyService()
        
        # Load keywords from prompts config
        intent_config = prompts.get('intent_analyzer', {})
        self.fact_keywords = intent_config.get('fact_keywords', [])
        self.instruction_keywords = intent_config.get('instruction_keywords', [])
        self.inspiration_keywords = intent_config.get('inspiration_keywords', [])
        self.branch_patterns = intent_config.get('branch_patterns', {})
        self.llm_enhance_prompt_template = intent_config.get('llm_enhance_prompt', '')
        
        # Log config loading
        if self.fact_keywords:
            logger.debug(f"Loaded {len(self.fact_keywords)} fact keywords from config")
        else:
            logger.warning("No intent_analyzer config found in prompts, using empty defaults")
    
    def analyze(self, query: str, history: List[Dict] = None) -> IntentTarget:
        """
        Analyze query and return IntentTarget with taxonomy coordinates.
        
        Args:
            query: User's current query
            history: Conversation history (optional)
            
        Returns:
            IntentTarget with detected topics, entities, branches, and intent
        """
        query_lower = query.lower()
        
        # 1. Extract known concepts from vocabulary
        concepts = self.vocabulary.extract_known_concepts(query)
        detected_topics = concepts.get("topics", [])
        detected_entities = concepts.get("entities", [])
        vocabulary_branches = concepts.get("branches", [])
        
        # 2. Classify intent using keywords from config
        intent_category = self._classify_intent(query_lower)
        
        # 3. Detect taxonomy branches using patterns from config
        detected_branches = self._detect_branches(query_lower, vocabulary_branches)
        
        # 4. Topic-to-Branch Inference (self-healing)
        detected_branches = self._infer_branches_from_topics(
            detected_topics, 
            detected_branches
        )
        
        # 5. Determine scope preference based on intent
        scope_preference = self._determine_scope(intent_category, detected_branches)
        
        # 6. Detect taxonomy roots from branches
        taxonomy_roots = self._roots_from_branches(detected_branches)
        
        # 7. Calculate confidence
        confidence = self._calculate_confidence(
            detected_topics, detected_entities, detected_branches
        )
        
        intent_target = IntentTarget(
            original_query=query,
            taxonomy_roots=taxonomy_roots,
            taxonomy_branches=detected_branches,
            detected_topics=detected_topics,
            detected_entities=detected_entities,
            scope_preference=scope_preference,
            intent_category=intent_category,
            confidence=confidence
        )
        
        logger.info(f"Intent Analysis: {intent_category}, branches={[b.value for b in detected_branches]}, "
                   f"topics={len(detected_topics)}, entities={len(detected_entities)}, confidence={confidence:.2f}")
        
        return intent_target
    
    def analyze_with_llm(self, query: str, history: List[Dict] = None) -> IntentTarget:
        """
        Enhanced analysis using LLM for complex queries.
        Falls back to rule-based analysis if LLM fails.
        """
        # First, do rule-based analysis
        base_intent = self.analyze(query, history)
        
        # If confidence is high enough, use rule-based result
        if base_intent.confidence >= 0.7:
            return base_intent
        
        # Otherwise, enhance with LLM
        try:
            enhanced = self._llm_enhance(query, base_intent)
            return enhanced
        except Exception as e:
            logger.warning(f"LLM enhancement failed: {e}, using rule-based result")
            return base_intent
    
    def _classify_intent(self, query_lower: str) -> str:
        """Classify query intent based on keyword patterns from config."""
        fact_score = sum(1 for kw in self.fact_keywords if kw in query_lower)
        instruction_score = sum(1 for kw in self.instruction_keywords if kw in query_lower)
        inspiration_score = sum(1 for kw in self.inspiration_keywords if kw in query_lower)
        
        # "hur skriver/gör/formulerar" patterns strongly boost INSTRUCTION
        if re.search(r'hur\s+(skriver|gör|formulerar|skapar|bygger)', query_lower):
            instruction_score += 3
        
        # "jag vill ha" patterns boost INSPIRATION (request, not question)
        if re.search(r'(jag vill|vi behöver|ge mig|visa mig)', query_lower):
            inspiration_score += 2
        
        # Question patterns boost FACT only if not instruction/inspiration
        if re.search(r'\?$', query_lower.strip()):
            if instruction_score == 0 and inspiration_score == 0:
                fact_score += 1
        
        # "vad är/hur mycket" are FACT questions
        if re.search(r'(vad är|hur mycket|vad kostar|får jag|måste jag)', query_lower):
            fact_score += 2
        
        # Determine winner
        if instruction_score > fact_score and instruction_score > inspiration_score:
            return "INSTRUCTION"
        elif inspiration_score > fact_score:
            return "INSPIRATION"
        elif fact_score > 0:
            return "FACT"
        else:
            return "INSPIRATION"  # Default to INSPIRATION for open-ended queries
    
    def _detect_branches(self, query_lower: str, vocabulary_branches: List[str]) -> List[TaxonomyBranch]:
        """Detect taxonomy branches from query text using patterns from config."""
        detected = set()
        
        # Add branches from vocabulary lookup
        for branch_name in vocabulary_branches:
            try:
                detected.add(TaxonomyBranch(branch_name))
            except ValueError:
                pass
        
        # Pattern-based detection from config
        for branch_name, patterns in self.branch_patterns.items():
            for pattern in patterns:
                if pattern.lower() in query_lower:
                    try:
                        detected.add(TaxonomyBranch(branch_name))
                    except ValueError:
                        pass
                    break
        
        # Default to ROLES if nothing detected
        if not detected:
            detected.add(TaxonomyBranch.ROLES)
        
        return list(detected)[:3]  # Max 3 branches
    
    def _infer_branches_from_topics(
        self, 
        detected_topics: List[str], 
        current_branches: List[TaxonomyBranch]
    ) -> List[TaxonomyBranch]:
        """
        Topic-to-Branch Inference - Infer missing branches from detected topics.
        
        This makes the system "self-healing": if the vocabulary knows that 
        "Grönland" is under LOCATIONS, we automatically add LOCATIONS branch.
        """
        inferred = set(current_branches)
        
        for topic in detected_topics:
            location = self.vocabulary.find_branch_for_topic(topic)
            if location:
                root, branch = location
                try:
                    branch_enum = TaxonomyBranch(branch)
                    if branch_enum not in inferred:
                        logger.debug(f"Inferred branch {branch} from topic '{topic}'")
                        inferred.add(branch_enum)
                except ValueError:
                    pass
        
        return list(inferred)[:3]  # Max 3 branches
    
    def _determine_scope(self, intent: str, branches: List[TaxonomyBranch]) -> List[ScopeContext]:
        """Determine scope preference based on intent and branches."""
        # FACT queries should prefer FRAMEWORK_SPECIFIC
        if intent == "FACT":
            return [ScopeContext.FRAMEWORK_SPECIFIC]
        
        # GOVERNANCE branch often involves legal context
        if TaxonomyBranch.GOVERNANCE in branches:
            return [ScopeContext.FRAMEWORK_SPECIFIC, ScopeContext.GENERAL_LEGAL]
        
        # INSPIRATION can use all scopes
        if intent == "INSPIRATION":
            return [
                ScopeContext.FRAMEWORK_SPECIFIC,
                ScopeContext.DOMAIN_KNOWLEDGE,
                ScopeContext.GENERAL_LEGAL
            ]
        
        # INSTRUCTION prefers framework-specific and domain knowledge
        if intent == "INSTRUCTION":
            return [ScopeContext.FRAMEWORK_SPECIFIC, ScopeContext.DOMAIN_KNOWLEDGE]
        
        # Default
        return [ScopeContext.FRAMEWORK_SPECIFIC, ScopeContext.DOMAIN_KNOWLEDGE]
    
    def _roots_from_branches(self, branches: List[TaxonomyBranch]) -> List[TaxonomyRoot]:
        """Determine taxonomy roots from detected branches."""
        roots = set()
        for branch in branches:
            for root, valid in VALID_BRANCHES.items():
                if branch in valid:
                    roots.add(root)
                    break
        
        return list(roots)
    
    def _calculate_confidence(
        self, 
        topics: List[str], 
        entities: List[str], 
        branches: List[TaxonomyBranch]
    ) -> float:
        """Calculate confidence score based on matches."""
        score = 0.3  # Base score
        
        # Topics found
        if topics:
            score += min(0.3, len(topics) * 0.1)
        
        # Entities found
        if entities:
            score += min(0.2, len(entities) * 0.1)
        
        # Branches detected (beyond default)
        if len(branches) > 1:
            score += 0.1
        
        return min(1.0, score)
    
    def _llm_enhance(self, query: str, base_intent: IntentTarget) -> IntentTarget:
        """Use LLM to enhance intent analysis for ambiguous queries."""
        if not self.llm_enhance_prompt_template:
            logger.warning("No LLM enhance prompt template configured")
            return base_intent
        
        vocab_context = self.vocabulary.get_prompt_context()
        
        # Format the prompt from config
        prompt = self.llm_enhance_prompt_template.format(
            query=query,
            vocab_context=vocab_context,
            current_intent=base_intent.intent_category,
            current_branches=[b.value for b in base_intent.taxonomy_branches],
            current_topics=base_intent.detected_topics
        )
        
        resp = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        result = json.loads(resp.text)
        
        # Parse LLM response into IntentTarget
        branches = []
        for b in result.get("taxonomy_branches", []):
            try:
                branches.append(TaxonomyBranch(b))
            except ValueError:
                pass
        
        if not branches:
            branches = base_intent.taxonomy_branches
        
        # Apply Topic-to-Branch Inference on LLM results too
        detected_topics = result.get("detected_topics", base_intent.detected_topics)
        branches = self._infer_branches_from_topics(detected_topics, branches)
        
        return IntentTarget(
            original_query=query,
            taxonomy_roots=self._roots_from_branches(branches),
            taxonomy_branches=branches,
            detected_topics=detected_topics,
            detected_entities=result.get("detected_entities", base_intent.detected_entities),
            scope_preference=self._determine_scope(
                result.get("intent_category", base_intent.intent_category),
                branches
            ),
            intent_category=result.get("intent_category", base_intent.intent_category),
            confidence=result.get("confidence", 0.7)
        )
