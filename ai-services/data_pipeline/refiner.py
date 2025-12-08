"""
Pipeline 2.0 - Refiner

Förbättrar befintliga Smart Blocks när svaret kan bli bättre (verdict: IMPROVE).

1. Hittar befintligt block (via sources från Tester)
2. Analyserar vad som kan förbättras
3. Uppdaterar block med bättre tags, exempel, tydligare formulering
4. Upsertar till index

Input: TestResult med verdict=IMPROVE
Output: Uppdaterat Smart Block
"""

import os
import re
import json
import yaml
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from google import genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
AI_SERVICES_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config" / "pipeline_v2_config.yaml"


def load_config() -> Dict:
    """Ladda pipeline config."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def find_block_file(source_name: str, lake_dir: Path) -> Optional[Path]:
    """Hitta block-fil baserat på source name."""
    # Prova exakt match först
    matches = list(lake_dir.glob(f"*{source_name}*"))
    if matches:
        return matches[0]
    
    # Prova utan extension
    base_name = Path(source_name).stem
    matches = list(lake_dir.glob(f"*{base_name}*"))
    if matches:
        return matches[0]
    
    return None


def parse_smart_block(file_path: Path) -> Dict:
    """Parse ett Smart Block från fil."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split YAML frontmatter och content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_str = parts[1]
            markdown = parts[2].strip()
            metadata = yaml.safe_load(yaml_str)
            return {
                'metadata': metadata,
                'content': markdown,
                'file_path': file_path
            }
    
    return {
        'metadata': {},
        'content': content,
        'file_path': file_path
    }


def save_updated_block(block_data: Dict, file_path: Path):
    """Spara uppdaterat block."""
    metadata = block_data['metadata']
    content = block_data['content']
    
    yaml_str = yaml.dump(metadata, allow_unicode=True, default_flow_style=False)
    full_content = f"---\n{yaml_str}---\n\n{content}"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    logger.info(f"Updated block: {file_path.name}")


async def analyze_improvement_needed(
    client: genai.Client,
    question: str,
    bot_response: str,
    judge_reasoning: str,
    current_block: Dict,
    model_name: str
) -> Dict:
    """
    Analysera vad som behöver förbättras i blocket.
    """
    
    prompt = """Du är expert på att förbättra Smart Blocks för P-Bot.

FRÅGA SOM STÄLLDES:
{question}

BOTTENS SVAR (som bedömdes som INCOMPLETE/WRONG):
{bot_response}

DOMARENS MOTIVERING:
{judge_reasoning}

NUVARANDE BLOCK METADATA:
{metadata}

NUVARANDE BLOCK INNEHÅLL:
{content}

UPPGIFT:
Föreslå förbättringar för att blocket ska kunna svara bättre på frågan.

OUTPUT FORMAT (JSON):
{{
  "improvements": {{
    "add_topic_tags": ["nya", "taggar", "att", "lägga", "till"],
    "add_examples": ["Nytt exempel att lägga till"],
    "content_suggestion": "Förslag på förbättrat innehåll (eller null om OK)",
    "reasoning": "Kort motivering av förbättringarna"
  }}
}}
""".format(
        question=question,
        bot_response=bot_response[:2000],
        judge_reasoning=judge_reasoning,
        metadata=json.dumps(current_block['metadata'], ensure_ascii=False, indent=2),
        content=current_block['content'][:3000]
    )

    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3
            }
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        logger.error(f"Improvement analysis error: {e}")
        return {"improvements": {}}


def apply_improvements(block_data: Dict, improvements: Dict) -> Dict:
    """Applicera förbättringar på blocket."""
    imp = improvements.get('improvements', {})
    
    # Lägg till nya topic_tags
    new_tags = imp.get('add_topic_tags', [])
    if new_tags:
        current_tags = block_data['metadata'].get('topic_tags', [])
        # Undvik duplicat
        for tag in new_tags:
            if tag not in current_tags:
                current_tags.append(tag)
        block_data['metadata']['topic_tags'] = current_tags
        logger.info(f"  Added {len(new_tags)} new topic_tags")
    
    # Lägg till nya examples
    new_examples = imp.get('add_examples', [])
    if new_examples:
        current_examples = block_data['metadata'].get('examples', [])
        for ex in new_examples:
            if ex not in current_examples:
                current_examples.append(ex)
        block_data['metadata']['examples'] = current_examples
        logger.info(f"  Added {len(new_examples)} new examples")
    
    # Uppdatera content om föreslaget
    content_suggestion = imp.get('content_suggestion')
    if content_suggestion and content_suggestion != "null":
        # Lägg till som tillägg, inte ersätt
        block_data['content'] += f"\n\n## Tillägg\n\n{content_suggestion}"
        logger.info("  Added content suggestion")
    
    return block_data


def upsert_to_index(block_data: Dict, index_dir: Path):
    """Upsert uppdaterat block till index."""
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        metadata = block_data['metadata']
        content = block_data['content']
        block_uuid = metadata.get('uuid', str(block_data['file_path']))
        
        # ChromaDB
        chroma_path = index_dir / "chroma"
        client = chromadb.PersistentClient(path=str(chroma_path))
        collection = client.get_or_create_collection(
            name="adda_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Embedding
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(content).tolist()
        
        # Upsert
        collection.upsert(
            ids=[block_uuid],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "source_file": metadata.get('source_file', ''),
                "authority_level": metadata.get('authority_level', 'PRIMARY'),
                "block_type": metadata.get('block_type', 'DEFINITION'),
                "taxonomy_branch": metadata.get('taxonomy_branch', ''),
                "topic_tags": ",".join(metadata.get('topic_tags', [])),
                "suggested_phase": ",".join(metadata.get('suggested_phase', []))
            }]
        )
        
        logger.info(f"  Upserted to index: {block_uuid[:8]}...")
        
    except ImportError as e:
        logger.warning(f"ChromaDB not available: {e}")
    except Exception as e:
        logger.error(f"Index upsert error: {e}")


async def refine_block(
    improve_result: Dict,
    config: Dict,
    lake_dir: Path,
    index_dir: Path
) -> bool:
    """
    Förbättra ett befintligt block.
    
    Returns: True om lyckades, False annars
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")
    
    client = genai.Client(api_key=api_key)
    model_name = config.get('models', {}).get('creator', 'gemini-2.0-flash')
    
    question = improve_result['question']
    bot_response = improve_result['bot_response']
    judge_reasoning = improve_result['judge_reasoning']
    sources = improve_result.get('sources', [])
    
    logger.info(f"Refining block for: {question[:50]}...")
    
    if not sources:
        logger.warning("  No sources to refine")
        return False
    
    # Hitta första source-blocket
    block_file = None
    for source in sources:
        block_file = find_block_file(source, lake_dir)
        if block_file:
            break
    
    if not block_file:
        logger.warning(f"  Could not find block file for sources: {sources}")
        return False
    
    # Parse blocket
    block_data = parse_smart_block(block_file)
    
    # Analysera förbättringar
    improvements = await analyze_improvement_needed(
        client=client,
        question=question,
        bot_response=bot_response,
        judge_reasoning=judge_reasoning,
        current_block=block_data,
        model_name=model_name
    )
    
    # Applicera
    updated_block = apply_improvements(block_data, improvements)
    
    # Spara
    save_updated_block(updated_block, block_file)
    
    # Upsert
    upsert_to_index(updated_block, index_dir)
    
    return True


async def process_all_improvements(
    test_results_path: Path,
    config: Dict,
    max_items: Optional[int] = None
) -> int:
    """
    Processa alla IMPROVE-resultat.
    
    Returns: Antal förbättrade blocks
    """
    # Ladda testresultat
    with open(test_results_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Filtrera IMPROVE
    improves = [r for r in test_data['results'] if r['verdict'] == 'IMPROVE']
    
    if max_items:
        improves = improves[:max_items]
    
    logger.info(f"Processing {len(improves)} IMPROVE items...")
    
    # Paths
    lake_dir = AI_SERVICES_DIR / config['paths'].get('output_lake', 'storage/lake_v2')
    if not lake_dir.exists():
        lake_dir = AI_SERVICES_DIR / 'storage/lake'
    
    index_dir = AI_SERVICES_DIR / config['paths'].get('output_index', 'storage/index_v2')
    
    refined_count = 0
    
    for i, item in enumerate(improves):
        logger.info(f"Processing IMPROVE {i+1}/{len(improves)}")
        
        success = await refine_block(
            improve_result=item,
            config=config,
            lake_dir=lake_dir,
            index_dir=index_dir
        )
        
        if success:
            refined_count += 1
    
    logger.info(f"Refined {refined_count} blocks")
    return refined_count


async def main():
    """Main entry point for Refiner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline 2.0 - Refiner")
    parser.add_argument('--input', type=str, default='test_results.json',
                       help='Input fil från Tester')
    parser.add_argument('--max-items', type=int, help='Max antal IMPROVE att processa')
    args = parser.parse_args()
    
    config = load_config()
    
    input_path = SCRIPT_DIR / "output" / args.input
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Kör först: python -m data_pipeline_v2.tester")
        return
    
    await process_all_improvements(
        test_results_path=input_path,
        config=config,
        max_items=args.max_items
    )


if __name__ == "__main__":
    asyncio.run(main())







