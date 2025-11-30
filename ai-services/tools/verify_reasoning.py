#!/usr/bin/env python3
"""
Reasoning Engine Verification Script v5.2
Tests the full pipeline: IntentAnalyzer -> ContextBuilder -> Planner

Usage:
    python tools/verify_reasoning.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Clean output for verification
)
logger = logging.getLogger("VERIFY")

# Suppress noisy loggers
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    width = 70
    print(f"\n{char * width}")
    print(f" {text}")
    print(f"{char * width}")


def print_section(text: str):
    """Print a section header."""
    print(f"\n--- {text} ---")


def verify_vocabulary_service():
    """Test VocabularyService initialization."""
    print_header("STEP 0: Vocabulary Service")
    
    from app.services import VocabularyService
    
    vocab = VocabularyService()
    
    print(f"✓ Vocabulary loaded")
    print(f"  - Topics: {len(vocab.get_known_topics())}")
    print(f"  - Entities: {len(vocab.get_known_entities())}")
    print(f"  - Taxonomy roots: {list(vocab.taxonomy.keys())}")
    
    # Sample topics
    sample_topics = vocab.get_known_topics()[:10]
    print(f"\n  Sample topics: {sample_topics}")
    
    return vocab


def verify_intent_analyzer(vocab):
    """Test IntentAnalyzer with scenarios."""
    print_header("STEP 1: Intent Analysis")
    
    from app.components import IntentAnalyzerComponent
    from google import genai
    import os
    import yaml
    from dotenv import load_dotenv
    
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Load prompts from config (IMPORTANT!)
    base_dir = Path(__file__).resolve().parent.parent
    prompts_path = base_dir / "config" / "assistant_prompts.yaml"
    
    with open(prompts_path, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f)
    
    print(f"✓ Loaded prompts from config")
    intent_config = prompts.get('intent_analyzer', {})
    print(f"  - fact_keywords: {len(intent_config.get('fact_keywords', []))} loaded")
    print(f"  - branch_patterns: {len(intent_config.get('branch_patterns', {}))} branches")
    
    # Create analyzer with prompts from config
    analyzer = IntentAnalyzerComponent(client, "gemini-2.0-flash-lite", prompts)
    
    # Test scenarios
    scenarios = [
        {
            "query": "Jag vill ha en projektledare i Grönland.",
            "expected_branches": ["LOCATIONS", "ROLES"],
            "expected_intent": "INSPIRATION",
            "description": "Geografi-fråga - ska hitta LOCATIONS"
        },
        {
            "query": "Vad är takpriset för en senior utvecklare?",
            "expected_branches": ["FINANCIALS"],
            "expected_intent": "FACT",
            "description": "Prisfråga - ska hitta FINANCIALS"
        },
        {
            "query": "Får jag göra direktupphandling på 500 000 kr?",
            "expected_branches": ["STRATEGY", "GOVERNANCE"],
            "expected_intent": "FACT",
            "description": "Strategi/regelfråga - ska hitta STRATEGY"
        },
        {
            "query": "Hur skriver jag en kravspecifikation?",
            "expected_branches": ["ARTIFACTS"],
            "expected_intent": "INSTRUCTION",
            "description": "Instruktionsfråga - ska hitta ARTIFACTS"
        },
        {
            "query": "Ge mig exempel på hur andra har upphandlat arkitekter.",
            "expected_branches": ["ROLES"],
            "expected_intent": "INSPIRATION",
            "description": "Exempel-fråga - ska vara INSPIRATION"
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print_section(f"Scenario {i}: {scenario['description']}")
        print(f"Query: \"{scenario['query']}\"")
        
        intent = analyzer.analyze(scenario['query'])
        
        print(f"\n  IntentTarget:")
        print(f"    - intent_category: {intent.intent_category}")
        print(f"    - taxonomy_roots: {[r.value for r in intent.taxonomy_roots]}")
        print(f"    - taxonomy_branches: {[b.value for b in intent.taxonomy_branches]}")
        print(f"    - detected_topics: {intent.detected_topics}")
        print(f"    - detected_entities: {intent.detected_entities}")
        print(f"    - scope_preference: {[s.value for s in intent.scope_preference]}")
        print(f"    - confidence: {intent.confidence:.2f}")
        print(f"    - should_block_secondary: {intent.should_block_secondary()}")
        
        # Check expectations
        detected_branches = [b.value for b in intent.taxonomy_branches]
        branch_match = any(b in detected_branches for b in scenario['expected_branches'])
        intent_match = intent.intent_category == scenario['expected_intent']
        
        status = "✓" if (branch_match and intent_match) else "⚠"
        print(f"\n  {status} Expected branches: {scenario['expected_branches']} -> Got: {detected_branches}")
        print(f"  {status} Expected intent: {scenario['expected_intent']} -> Got: {intent.intent_category}")
        
        results.append({
            "scenario": scenario['description'],
            "intent": intent,
            "branch_match": branch_match,
            "intent_match": intent_match
        })
    
    return analyzer, results


def verify_context_builder(analyzer, intent_results):
    """Test ContextBuilder with the intents from previous step."""
    print_header("STEP 2: Context Building")
    
    from app.components import ContextBuilderComponent
    from pathlib import Path
    import chromadb
    from chromadb.utils import embedding_functions
    import kuzu
    
    # Initialize dependencies
    base_dir = Path(__file__).resolve().parent.parent
    lake_path = base_dir / "data_pipeline" / "output"
    chroma_path = base_dir / "storage" / "index" / "chroma"
    kuzu_path = base_dir / "storage" / "index" / "kuzu"
    
    # ChromaDB
    chroma_client = chromadb.PersistentClient(path=str(chroma_path))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = chroma_client.get_collection(
        name="adda_knowledge",
        embedding_function=embed_fn
    )
    
    # Kuzu
    db = kuzu.Database(str(kuzu_path))
    conn = kuzu.Connection(db)
    
    # Create ContextBuilder
    builder = ContextBuilderComponent(lake_path, collection, conn)
    
    context_results = []
    
    for result in intent_results:
        intent = result['intent']
        print_section(f"Context for: {result['scenario']}")
        print(f"Query: \"{intent.original_query}\"")
        print(f"Ghost Mode (block SECONDARY): {intent.should_block_secondary()}")
        
        # Build context
        context = builder.build_context(intent)
        
        print(f"\n  Retrieved {len(context)} documents:")
        
        # Group by source type
        by_source = {}
        for doc_id, doc in context.items():
            source = doc.get('source', 'UNKNOWN')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(doc)
        
        for source, docs in by_source.items():
            print(f"\n  [{source}] ({len(docs)} hits):")
            for doc in docs[:3]:  # Show max 3 per source
                auth = doc.get('authority', '?')
                scope = doc.get('scope_context', '?')
                branch = doc.get('taxonomy_branch', '?')
                filename = doc.get('filename', '?')
                doc_type = doc.get('type', '?')
                
                print(f"    - {filename}")
                print(f"      type={doc_type}, authority={auth}, scope={scope}, branch={branch}")
        
        # Summary
        authorities = set(doc.get('authority', '?') for doc in context.values())
        scopes = set(doc.get('scope_context', '?') for doc in context.values())
        
        print(f"\n  Summary:")
        print(f"    - Authority levels: {authorities}")
        print(f"    - Scope contexts: {scopes}")
        
        # Verify Ghost Mode
        if intent.should_block_secondary():
            has_secondary = 'SECONDARY' in authorities
            status = "⚠ VIOLATION" if has_secondary else "✓ OK"
            print(f"    - Ghost Mode check: {status} (SECONDARY should be blocked)")
        
        context_results.append({
            "scenario": result['scenario'],
            "intent": intent,
            "context": context
        })
    
    return builder, context_results


def verify_planner(context_results):
    """Test Planner (Logic Layer) with context from previous step."""
    print_header("STEP 3: Reasoning (Planner)")
    
    from app.components import PlannerComponent
    from google import genai
    import os
    import yaml
    from dotenv import load_dotenv
    
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Load prompts
    base_dir = Path(__file__).resolve().parent.parent
    prompts_path = base_dir / "config" / "assistant_prompts.yaml"
    
    with open(prompts_path, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f)
    
    print(f"✓ Loaded planner.system_prompt from config")
    
    # Create Planner
    planner = PlannerComponent(client, "gemini-2.0-flash-lite", prompts)
    
    for result in context_results[:3]:  # Test first 3 only (LLM calls are slow)
        intent = result['intent']
        context = result['context']
        
        print_section(f"Reasoning for: {result['scenario']}")
        print(f"Query: \"{intent.original_query}\"")
        print(f"Context docs: {len(context)}")
        
        if not context:
            print("  ⚠ No context - skipping planner")
            continue
        
        # Create plan
        plan = planner.create_plan(intent, context)
        
        print(f"\n  ReasoningPlan:")
        print(f"    - primary_conclusion: {plan.primary_conclusion[:100]}...")
        print(f"    - policy_check: {plan.policy_check}")
        print(f"    - tone_instruction: {plan.tone_instruction}")
        print(f"    - target_step: {plan.target_step}")
        print(f"    - missing_info: {plan.missing_info}")
        
        if plan.conflict_resolution:
            print(f"    - conflict_resolution: {plan.conflict_resolution}")
        if plan.data_validation:
            print(f"    - data_validation: {plan.data_validation}")
        
        print(f"    - requires_warning: {plan.requires_warning()}")
        print(f"    - primary_sources: {plan.primary_sources[:3]}")
        print(f"    - secondary_sources: {plan.secondary_sources[:3]}")


def main():
    """Run full verification."""
    print_header("REASONING ENGINE VERIFICATION v5.2", "█")
    print("Testing full pipeline: Intent -> Context -> Planner")
    
    try:
        # Step 0: Vocabulary
        vocab = verify_vocabulary_service()
        
        # Step 1: Intent Analysis
        analyzer, intent_results = verify_intent_analyzer(vocab)
        
        # Step 2: Context Building
        builder, context_results = verify_context_builder(analyzer, intent_results)
        
        # Step 3: Planner (Logic Layer)
        verify_planner(context_results)
        
        # Summary
        print_header("VERIFICATION COMPLETE", "█")
        
        passed = sum(1 for r in intent_results if r['branch_match'] and r['intent_match'])
        total = len(intent_results)
        
        print(f"\nIntent Analysis: {passed}/{total} scenarios passed")
        print(f"Context Building: {len(context_results)} scenarios processed")
        print(f"Planner: Tested on first 3 scenarios (LLM calls)")
        
        if passed == total:
            print("\n✓ All tests passed!")
        else:
            print("\n⚠ Some tests failed - review output above")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

