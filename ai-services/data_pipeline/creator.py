"""
Pipeline 2.0 - Creator

Skapar nya Smart Blocks när P-Bot inte kan svara (verdict: GAP).

1. Läser Document Registry för att välja rätt FULL_DOCUMENT
2. Läser det dokumentet
3. Skapar Smart Block med svaret
4. Upsertar till ChromaDB + Kuzu

Input: TestResult med verdict=GAP
Output: Nytt Smart Block i lake_v2
"""

import os
import re
import json
import uuid
import yaml
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from google import genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
AI_SERVICES_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config" / "pipeline_v2_config.yaml"
REGISTRY_PATH = SCRIPT_DIR / "config" / "document_registry.yaml"


@dataclass
class SmartBlock:
    """Ett Smart Block för Lake."""
    uuid: str
    source_file: str
    authority_level: str
    block_type: str
    taxonomy_root: str
    taxonomy_branch: str
    scope_context: str
    suggested_phase: List[str]
    topic_tags: List[str]
    constraints: List[Dict] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    content_markdown: str = ""
    
    def to_markdown(self) -> str:
        """Konvertera till Markdown med YAML frontmatter."""
        yaml_data = {
            'uuid': self.uuid,
            'doc_type': 'smart_block',
            'source_file': self.source_file,
            'authority_level': self.authority_level,
            'block_type': self.block_type,
            'taxonomy_root': self.taxonomy_root,
            'taxonomy_branch': self.taxonomy_branch,
            'scope_context': self.scope_context,
            'suggested_phase': self.suggested_phase,
            'topic_tags': self.topic_tags,
        }
        
        if self.constraints:
            yaml_data['constraints'] = self.constraints
        if self.examples:
            yaml_data['examples'] = self.examples
        
        yaml_str = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)
        
        return f"---\n{yaml_str}---\n\n{self.content_markdown}"
    
    def get_filename(self) -> str:
        """Generera filnamn enligt konvention."""
        phase = self.suggested_phase[0] if self.suggested_phase else "general"
        phase_short = phase.replace("step_", "") if phase.startswith("step_") else phase
        short_uuid = self.uuid[:8]
        return f"{phase_short}_{self.block_type}_PRIMARY_{short_uuid}.md"


def load_config() -> Dict:
    """Ladda pipeline config."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_document_registry() -> Dict:
    """Ladda document registry med summaries."""
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def read_full_document(file_path: Path) -> Optional[str]:
    """Läs ett FULL_DOCUMENT från Lake."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ta bort YAML frontmatter
            if '---' in content:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    return parts[2].strip()
            return content
    except Exception as e:
        logger.error(f"Could not read {file_path}: {e}")
        return None


async def select_relevant_documents(
    client: genai.Client,
    question: str,
    registry: Dict,
    model_name: str
) -> List[str]:
    """
    Använd LLM för att välja FLERA relevanta dokument från registry.
    
    Returns: Lista med document_ids (1-3 dokument)
    """
    # Bygg summary-lista
    summaries = []
    for doc in registry.get('documents', []):
        summaries.append(f"ID: {doc['id']}\n{doc['summary']}")
    
    prompt = """Du ska välja VILKA dokument som behövs för att svara KOMPLETT på en fråga.

FRÅGA:
{question}

TILLGÄNGLIGA DOKUMENT:
{summaries}

ANALYS:
1. Vad frågar användaren om? (t.ex. villkor, konsekvenser, process)
2. Behövs INFO om VILLKOR/REGLER? → välj relevant dokument
3. Behövs INFO om KONSEKVENSER (vite, hävning)? → välj kontraktsvillkor
4. Behövs INFO om PROCESS? → välj avropsvagledning

OUTPUT FORMAT (JSON):
{{
  "documents": ["doc_id_1", "doc_id_2"],
  "reasoning": "Kort motivering varför dessa dokument behövs"
}}

Välj 1-3 dokument. Om frågan är enkel räcker 1. Om frågan handlar om både villkor OCH konsekvenser behövs 2+.
Om ingen passar, returnera tom lista.
""".format(question=question, summaries="\n\n".join(summaries))

    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )
        
        result = json.loads(response.text)
        doc_ids = result.get('documents', [])
        
        # Validera att alla är giltiga IDs
        valid_ids = [d['id'] for d in registry.get('documents', [])]
        validated = []
        for doc_id in doc_ids:
            if doc_id in valid_ids:
                validated.append(doc_id)
            else:
                # Försök fuzzy match
                for vid in valid_ids:
                    if vid.lower() in doc_id.lower() or doc_id.lower() in vid.lower():
                        validated.append(vid)
                        break
        
        return validated[:3]  # Max 3 dokument
            
    except Exception as e:
        logger.error(f"Document selection error: {e}")
        return []


async def create_smart_blocks(
    client: genai.Client,
    question: str,
    documents_content: Dict[str, str],  # {source_file: content}
    phase: str,
    anonymized_example: Optional[str],
    model_name: str
) -> List[SmartBlock]:
    """
    Använd LLM för att skapa ETT ELLER FLERA Smart Blocks från dokumenten.
    
    Returnerar flera block om frågan kräver det (t.ex. VILLKOR + KONSEKVENS).
    """
    
    # Kombinera dokument-innehåll
    combined_content = ""
    source_files = list(documents_content.keys())
    for source, content in documents_content.items():
        combined_content += f"\n\n=== KÄLLA: {source} ===\n{content[:8000]}"
    
    prompt = """Du är en expert på att skapa Smart Blocks för Addas P-Bot kunskapsbas.

FRÅGA SOM SKA KUNNA BESVARAS:
{question}

KÄLLDOKUMENT:
{combined_content}

RELEVANT STEG I PROCESSEN: {phase}

{example_section}

UPPGIFT:
Skapa ETT eller FLERA Smart Blocks som TILLSAMMANS kan svara på frågan KOMPLETT.

ANALYSERA FÖRST:
1. Handlar frågan om VILLKOR/REGLER? → Skapa ett VILLKOR-block
2. Handlar frågan om KONSEKVENSER (vite, hävning, sanktioner)? → Skapa ett KONSEKVENS-block
3. Handlar frågan om PROCESS/HUR? → Skapa ett INSTRUKTION-block

Om frågan handlar om BÅDE villkor OCH konsekvenser → Skapa TVÅ separata block!

OUTPUT FORMAT (JSON):
{{
  "blocks": [
    {{
      "block_type": "RULE" | "DEFINITION" | "INSTRUCTION",
      "focus": "VILLKOR" | "KONSEKVENS" | "PROCESS" | "DEFINITION",
      "taxonomy_root": "BUSINESS_CONCEPTS" | "DOMAIN_OBJECTS" | "PROCESS",
      "taxonomy_branch": "STRATEGY" | "FINANCIALS" | "ROLES" | "LOCATIONS" | "PHASES" | "GOVERNANCE",
      "topic_tags": ["tag1", "tag2", ...],
      "linking_terms": ["term1", "term2"],  // Termer som länkar till andra block
      "title": "Kort titel",
      "content": "Markdown-innehåll",
      "source_file": "vilken källa informationen kom från"
    }}
  ]
}}

VIKTIGT FÖR LÄNKNING:
- Om du skapar ett VILLKOR-block som nämner "avtalsbrott" → lägg "avtalsbrott" i linking_terms
- Om du skapar ett KONSEKVENS-block → lägg samma linking_terms som i VILLKOR-blocket
- Detta gör att P-Bot kan hitta båda blocken via samma sökterm!

REGLER:
- Skapa 1-3 block beroende på frågans komplexitet
- Varje block ska vara ATOMÄRT (fokuserat på EN sak)
- topic_tags ska vara RIKA (5-10 taggar per block)
- Inkludera synonymer i topic_tags
""".format(
        question=question,
        combined_content=combined_content,
        phase=phase,
        example_section=f"ANONYMISERAT EXEMPEL FRÅN PRAKTIKEN:\n{anonymized_example}" if anonymized_example else ""
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
        
        result = json.loads(response.text)
        blocks_data = result.get('blocks', [])
        
        created_blocks = []
        for block_data in blocks_data:
            # Hitta rätt source_file
            source_file = block_data.get('source_file', source_files[0] if source_files else 'unknown')
            
            # Kombinera topic_tags med linking_terms
            all_tags = list(set(
                block_data.get('topic_tags', []) + 
                block_data.get('linking_terms', [])
            ))
            
            block = SmartBlock(
                uuid=str(uuid.uuid4()),
                source_file=source_file,
                authority_level="PRIMARY",
                block_type=block_data.get('block_type', 'DEFINITION'),
                taxonomy_root=block_data.get('taxonomy_root', 'BUSINESS_CONCEPTS'),
                taxonomy_branch=block_data.get('taxonomy_branch', 'STRATEGY'),
                scope_context="FRAMEWORK_SPECIFIC",
                suggested_phase=[phase] if phase else ["general"],
                topic_tags=all_tags,
                constraints=[],
                examples=[anonymized_example] if anonymized_example else [],
                content_markdown=f"# {block_data.get('title', 'Untitled')}\n\n{block_data.get('content', '')}"
            )
            created_blocks.append(block)
        
        return created_blocks
        
    except Exception as e:
        logger.error(f"Smart Block creation error: {e}")
        return []


def save_smart_block(block: SmartBlock, output_dir: Path) -> Path:
    """Spara Smart Block till lake_v2."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = block.get_filename()
    file_path = output_dir / filename
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(block.to_markdown())
    
    logger.info(f"Saved Smart Block: {filename}")
    return file_path


def upsert_to_index(block: SmartBlock, index_dir: Path):
    """
    Upsert Smart Block till ChromaDB + Kuzu.
    
    Detta gör att botten kan använda blocket direkt.
    """
    try:
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        # ChromaDB
        chroma_path = index_dir / "chroma"
        chroma_path.mkdir(parents=True, exist_ok=True)
        
        client = chromadb.PersistentClient(path=str(chroma_path))
        collection = client.get_or_create_collection(
            name="adda_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Embedding
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(block.content_markdown).tolist()
        
        # Upsert
        collection.upsert(
            ids=[block.uuid],
            embeddings=[embedding],
            documents=[block.content_markdown],
            metadatas=[{
                "source_file": block.source_file,
                "authority_level": block.authority_level,
                "block_type": block.block_type,
                "taxonomy_branch": block.taxonomy_branch,
                "topic_tags": ",".join(block.topic_tags),
                "suggested_phase": ",".join(block.suggested_phase)
            }]
        )
        
        logger.info(f"Upserted to ChromaDB: {block.uuid}")
        
    except ImportError as e:
        logger.warning(f"ChromaDB/SentenceTransformer not available: {e}")
    except Exception as e:
        logger.error(f"Index upsert error: {e}")


async def create_blocks_for_gap(
    gap_result: Dict,
    config: Dict,
    registry: Dict,
    lake_dir: Path,
    output_dir: Path,
    index_dir: Path
) -> List[SmartBlock]:
    """
    Skapa ETT ELLER FLERA Smart Blocks för en GAP.
    
    1. Välj relevanta dokument via registry (1-3 st)
    2. Läs dokumenten
    3. Skapa Smart Blocks (kan vara flera om frågan kräver det)
    4. Spara + upsert alla
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")
    
    client = genai.Client(api_key=api_key)
    model_name = config.get('models', {}).get('creator', 'gemini-2.0-flash')
    
    question = gap_result['question']
    phase = gap_result.get('phase', 'step_1_intake')
    anonymized_example = gap_result.get('anonymized_example')
    
    logger.info(f"Creating block(s) for: {question[:50]}...")
    
    # 1. Välj FLERA dokument
    doc_ids = await select_relevant_documents(client, question, registry, model_name)
    
    if not doc_ids:
        logger.warning(f"No relevant documents found for: {question[:50]}")
        return []
    
    logger.info(f"  → Selected {len(doc_ids)} document(s): {doc_ids}")
    
    # 2. Läs alla valda dokument
    documents_content = {}
    for doc_id in doc_ids:
        doc_info = next((d for d in registry['documents'] if d['id'] == doc_id), None)
        if not doc_info:
            continue
        
        doc_path = lake_dir / doc_info['file']
        
        # Fuzzy match om exakt fil inte finns
        if not doc_path.exists():
            matches = list(lake_dir.glob(f"*{doc_id}*"))
            if matches:
                doc_path = matches[0]
            else:
                logger.warning(f"Document file not found: {doc_info['file']}")
                continue
        
        content = read_full_document(doc_path)
        if content:
            documents_content[doc_info['file']] = content
    
    if not documents_content:
        logger.error("No document content could be read")
        return []
    
    # 3. Skapa Smart Block(s) - kan vara flera!
    blocks = await create_smart_blocks(
        client=client,
        question=question,
        documents_content=documents_content,
        phase=phase,
        anonymized_example=anonymized_example,
        model_name=model_name
    )
    
    if not blocks:
        return []
    
    # 4. Spara och upsert alla block
    for block in blocks:
        save_smart_block(block, output_dir)
        upsert_to_index(block, index_dir)
    
    logger.info(f"  → Created {len(blocks)} block(s)")
    return blocks


async def process_all_gaps(
    test_results_path: Path,
    config: Dict,
    max_gaps: Optional[int] = None
) -> List[SmartBlock]:
    """
    Processa alla GAPs från testresultat.
    
    Returnerar alla skapade block (kan vara fler än antal GAPs om multi-block skapas).
    """
    # Ladda testresultat
    with open(test_results_path, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # Filtrera GAPs
    gaps = [r for r in test_data['results'] if r['verdict'] == 'GAP']
    
    if max_gaps:
        gaps = gaps[:max_gaps]
    
    logger.info(f"Processing {len(gaps)} GAPs...")
    
    # Ladda registry
    registry = load_document_registry()
    
    # Paths
    lake_dir = AI_SERVICES_DIR / config['paths'].get('primary_fulldocs', 'storage/lake')
    output_dir = AI_SERVICES_DIR / config['paths'].get('output_lake', 'storage/lake_v2')
    index_dir = AI_SERVICES_DIR / config['paths'].get('output_index', 'storage/index_v2')
    
    created_blocks = []
    
    for i, gap in enumerate(gaps):
        logger.info(f"Processing GAP {i+1}/{len(gaps)}")
        
        # Kan returnera flera block!
        blocks = await create_blocks_for_gap(
            gap_result=gap,
            config=config,
            registry=registry,
            lake_dir=lake_dir,
            output_dir=output_dir,
            index_dir=index_dir
        )
        
        created_blocks.extend(blocks)
    
    logger.info(f"Created {len(created_blocks)} new Smart Blocks from {len(gaps)} GAPs")
    return created_blocks


async def main():
    """Main entry point for Creator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline 2.0 - Creator")
    parser.add_argument('--input', type=str, default='test_results.json',
                       help='Input fil från Tester')
    parser.add_argument('--max-gaps', type=int, help='Max antal GAPs att processa')
    args = parser.parse_args()
    
    config = load_config()
    
    input_path = SCRIPT_DIR / "output" / args.input
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Kör först: python -m data_pipeline_v2.tester")
        return
    
    await process_all_gaps(
        test_results_path=input_path,
        config=config,
        max_gaps=args.max_gaps
    )


if __name__ == "__main__":
    asyncio.run(main())

