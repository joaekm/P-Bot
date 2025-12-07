"""
Pipeline 2.0 - Deduplicator (LLM-driven)

Smart deduplicering med LLM för intelligent merge:
- UNION av topic_tags
- LÄNGSTA/BÄSTA content
- ALLA examples
- LLM rensar och strukturerar

Körs efter batch-körning för att städa upp duplikat.

Usage:
    python -m data_pipeline_v2.deduplicator --threshold 0.85
"""

import os
import re
import yaml
import json
import uuid
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
AI_SERVICES_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config" / "pipeline_v2_config.yaml"

# LLM Merge Prompt
MERGE_PROMPT = """Du är en expert på att strukturera kunskapsblock för ett RAG-system.

UPPGIFT:
Slå samman {n_blocks} Smart Blocks till ETT rent, välstrukturerat block.

KÄLLBLOCK:
{blocks_content}

REGLER FÖR SAMMANSLAGNING:

1. **topic_tags** (UNION - behåll ALLA unika):
   - Samla ALLA topic_tags från alla block
   - Ta bort dubbletter
   - Behåll endast relevanta sökord (substantiv, verb, begrepp)
   - EXKLUDERA: filnamn, UUIDs, faser (step_X_name)

2. **suggested_phase** (MEST SPECIFIK):
   - Välj den mest specifika fasen från blocken
   - Prioritet: step_1_intake > step_2_level > step_3_volume > step_4_strategy > general
   - Om alla är "general", behåll "general"

3. **content_markdown** (BÄSTA + KOMPLETT):
   - Välj det LÄNGSTA och mest informativa innehållet
   - Måste börja med markdown-rubrik (# ...)
   - Får ENDAST innehålla ren markdown (text, listor, rubriker)
   - FÅR EJ innehålla: YAML-syntax, filnamn, UUIDs, metadata

4. **block_type** (BEHÅLL DOMINANT):
   - Om majoriteten är DEFINITION → DEFINITION
   - Om majoriteten är RULE → RULE  
   - Om majoriteten är INSTRUCTION → INSTRUCTION

5. **examples** (UNION - behåll ALLA unika):
   - Samla alla unika exempel från blocken

OUTPUT FORMAT (strikt JSON):
{{
  "topic_tags": ["tag1", "tag2", "tag3"],
  "suggested_phase": "step_2_level",
  "block_type": "DEFINITION",
  "content_markdown": "# Rubrik\\n\\nRen markdown utan YAML...",
  "examples": ["exempel1", "exempel2"]
}}

VIKTIGT: Returnera ENDAST JSON, ingen annan text."""


@dataclass
class SmartBlock:
    """Representation av ett Smart Block."""
    uuid: str
    filepath: Path
    source_file: str
    authority_level: str
    block_type: str
    taxonomy_root: str
    taxonomy_branch: str
    scope_context: str
    suggested_phase: List[str]
    topic_tags: List[str]
    examples: List[str]
    content_markdown: str
    embedding: np.ndarray = None
    
    @classmethod
    def from_file(cls, filepath: Path) -> 'SmartBlock':
        """Ladda block från fil."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                metadata = yaml.safe_load(parts[1]) or {}
                markdown = parts[2].strip()
            else:
                metadata = {}
                markdown = content
        else:
            metadata = {}
            markdown = content
        
        # Ensure lists are actually lists
        topic_tags = metadata.get('topic_tags', [])
        if topic_tags is None:
            topic_tags = []
        elif isinstance(topic_tags, str):
            topic_tags = [t.strip() for t in topic_tags.split(',')]
        
        suggested_phase = metadata.get('suggested_phase', [])
        if suggested_phase is None:
            suggested_phase = []
        elif isinstance(suggested_phase, str):
            suggested_phase = [suggested_phase]
        
        examples = metadata.get('examples', [])
        if examples is None:
            examples = []
        elif isinstance(examples, str):
            examples = [examples]
        
        return cls(
            uuid=metadata.get('uuid', str(uuid.uuid4())),
            filepath=filepath,
            source_file=metadata.get('source_file', ''),
            authority_level=metadata.get('authority_level', 'PRIMARY'),
            block_type=metadata.get('block_type', 'DEFINITION'),
            taxonomy_root=metadata.get('taxonomy_root', 'DOMAIN_OBJECTS'),
            taxonomy_branch=metadata.get('taxonomy_branch', 'STRATEGY'),
            scope_context=metadata.get('scope_context', 'FRAMEWORK_SPECIFIC'),
            suggested_phase=suggested_phase,
            topic_tags=topic_tags,
            examples=examples,
            content_markdown=markdown
        )
    
    def to_markdown(self) -> str:
        """Konvertera tillbaka till markdown med YAML frontmatter."""
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
        
        if self.examples:
            yaml_data['examples'] = self.examples
        
        yaml_str = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)
        return f"---\n{yaml_str}---\n\n{self.content_markdown}"
    
    def to_summary(self) -> str:
        """Skapa en sammanfattning för LLM-prompten."""
        return f"""--- BLOCK ---
block_type: {self.block_type}
suggested_phase: {self.suggested_phase}
topic_tags: {self.topic_tags}
examples: {self.examples}
content:
{self.content_markdown}
--- END BLOCK ---"""


def load_all_blocks(lake_dir: Path) -> List[SmartBlock]:
    """Ladda alla Smart Blocks från lake."""
    blocks = []
    for filepath in lake_dir.glob("*.md"):
        try:
            block = SmartBlock.from_file(filepath)
            blocks.append(block)
        except Exception as e:
            logger.warning(f"Could not load {filepath}: {e}")
    
    logger.info(f"Loaded {len(blocks)} blocks from {lake_dir}")
    return blocks


def compute_embeddings(blocks: List[SmartBlock]) -> List[SmartBlock]:
    """Beräkna embeddings för alla block."""
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Kombinera content + tags för embedding
        texts = []
        for block in blocks:
            text = block.content_markdown + " " + " ".join(block.topic_tags)
            texts.append(text)
        
        logger.info("Computing embeddings...")
        embeddings = model.encode(texts, show_progress_bar=True)
        
        for i, block in enumerate(blocks):
            block.embedding = embeddings[i]
        
        return blocks
        
    except ImportError:
        logger.error("sentence_transformers not installed")
        return blocks


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Beräkna cosine similarity mellan två vektorer."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_duplicates(blocks: List[SmartBlock], threshold: float = 0.85) -> List[Tuple[int, int, float]]:
    """
    Hitta duplikat baserat på embedding-likhet.
    
    Returns: Lista med (index_a, index_b, similarity)
    """
    duplicates = []
    n = len(blocks)
    
    logger.info(f"Checking {n * (n-1) // 2} block pairs for duplicates...")
    
    for i in range(n):
        for j in range(i + 1, n):
            if blocks[i].embedding is None or blocks[j].embedding is None:
                continue
            
            sim = cosine_similarity(blocks[i].embedding, blocks[j].embedding)
            
            if sim >= threshold:
                duplicates.append((i, j, sim))
                logger.info(f"  Found duplicate: {blocks[i].filepath.name} <-> {blocks[j].filepath.name} ({sim:.2%})")
    
    return duplicates


async def merge_blocks_with_llm(
    cluster_blocks: List[SmartBlock],
    model_name: str = "gemini-2.0-flash"
) -> SmartBlock:
    """
    Använd LLM för att intelligent merga ett kluster av block.
    """
    try:
        from google import genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY")
        
        client = genai.Client(api_key=api_key)
        
        # Bygg block-sammanfattningar för prompten
        blocks_content = "\n\n".join(b.to_summary() for b in cluster_blocks)
        
        prompt = MERGE_PROMPT.format(
            n_blocks=len(cluster_blocks),
            blocks_content=blocks_content
        )
        
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        # Parsa JSON från response
        response_text = response.text.strip()
        
        # Ta bort eventuella markdown code blocks
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        result = json.loads(response_text)
        
        # Välj bästa source_file och taxonomi från klustret
        source_files = list(set(b.source_file for b in cluster_blocks if b.source_file))
        best_source = source_files[0] if source_files else "merged"
        
        # Skapa nytt merged block
        merged = SmartBlock(
            uuid=str(uuid.uuid4()),
            filepath=cluster_blocks[0].filepath,  # Kommer skrivas över
            source_file="; ".join(source_files[:3]) if len(source_files) > 1 else best_source,
            authority_level="PRIMARY",
            block_type=result.get("block_type", "DEFINITION"),
            taxonomy_root=cluster_blocks[0].taxonomy_root,
            taxonomy_branch=cluster_blocks[0].taxonomy_branch,
            scope_context="FRAMEWORK_SPECIFIC",
            suggested_phase=[result.get("suggested_phase", "general")] if isinstance(result.get("suggested_phase"), str) else result.get("suggested_phase", ["general"]),
            topic_tags=result.get("topic_tags", []),
            examples=result.get("examples", []),
            content_markdown=result.get("content_markdown", "# Merged Block\n\nContent unavailable.")
        )
        
        logger.info(f"  → LLM merged: {len(merged.topic_tags)} tags, {len(merged.content_markdown)} chars")
        return merged
        
    except Exception as e:
        logger.error(f"LLM merge failed: {e}")
        # Fallback: returnera första blocket
        return cluster_blocks[0]


async def deduplicate_blocks(
    blocks: List[SmartBlock], 
    duplicates: List[Tuple[int, int, float]],
    use_llm: bool = True
) -> Tuple[List[SmartBlock], List[SmartBlock], List[SmartBlock]]:
    """
    Processa duplikat och skapa merged blocks.
    
    Returns: (kept_blocks, merged_blocks, removed_blocks)
    """
    if not duplicates:
        return blocks, [], []
    
    # Bygg en graf av duplikat-kluster
    from collections import defaultdict
    
    # Union-Find för att hitta kluster
    parent = list(range(len(blocks)))
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    # Koppla ihop duplikat
    for i, j, _ in duplicates:
        union(i, j)
    
    # Gruppera block per kluster
    clusters = defaultdict(list)
    for i in range(len(blocks)):
        clusters[find(i)].append(i)
    
    kept_blocks = []
    merged_blocks = []
    removed_blocks = []
    
    for cluster_id, indices in clusters.items():
        if len(indices) == 1:
            # Inte ett duplikat
            kept_blocks.append(blocks[indices[0]])
        else:
            # Merge alla i klustret
            cluster_blocks = [blocks[i] for i in indices]
            logger.info(f"Merging cluster of {len(indices)} blocks:")
            for b in cluster_blocks:
                logger.info(f"  - {b.filepath.name}")
            
            if use_llm:
                # LLM-driven merge
                merged = await merge_blocks_with_llm(cluster_blocks)
            else:
                # Fallback: ta första
                merged = cluster_blocks[0]
            
            merged_blocks.append(merged)
            removed_blocks.extend(cluster_blocks)
    
    return kept_blocks, merged_blocks, removed_blocks


def save_results(
    lake_dir: Path,
    kept_blocks: List[SmartBlock],
    merged_blocks: List[SmartBlock],
    removed_blocks: List[SmartBlock],
    dry_run: bool = True
):
    """
    Spara resultat:
    - Ta bort duplikat-filer
    - Spara merged blocks
    """
    
    if dry_run:
        logger.info("=" * 60)
        logger.info("DRY RUN - Inga ändringar görs")
        logger.info("=" * 60)
    
    # Ta bort gamla duplikat-filer
    for block in removed_blocks:
        if dry_run:
            logger.info(f"Would DELETE: {block.filepath.name}")
        else:
            try:
                block.filepath.unlink()
                logger.info(f"Deleted: {block.filepath.name}")
            except Exception as e:
                logger.error(f"Could not delete {block.filepath}: {e}")
    
    # Spara merged blocks
    for block in merged_blocks:
        # Generera nytt filnamn
        phase = block.suggested_phase[0] if block.suggested_phase else "general"
        phase_short = phase.replace("step_", "") if phase.startswith("step_") else phase
        filename = f"{phase_short}_{block.block_type}_PRIMARY_MERGED_{block.uuid[:8]}.md"
        filepath = lake_dir / filename
        
        if dry_run:
            logger.info(f"Would CREATE: {filename}")
            logger.info(f"  topic_tags: {len(block.topic_tags)} tags")
            logger.info(f"  examples: {len(block.examples)}")
            logger.info(f"  content: {len(block.content_markdown)} chars")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(block.to_markdown())
            logger.info(f"Created: {filename}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("DEDUPLICATION SUMMARY")
    logger.info(f"  Kept unchanged: {len(kept_blocks)}")
    logger.info(f"  Merged: {len(merged_blocks)} (from {len(removed_blocks)} originals)")
    logger.info(f"  Final block count: {len(kept_blocks) + len(merged_blocks)}")
    logger.info("=" * 60)


async def run_deduplication(
    lake_dir: Path,
    threshold: float = 0.85,
    dry_run: bool = True,
    use_llm: bool = True
):
    """Main deduplication flow."""
    
    logger.info("=" * 60)
    logger.info("PIPELINE 2.0 - DEDUPLICATOR (LLM-driven)")
    logger.info(f"  Lake: {lake_dir}")
    logger.info(f"  Threshold: {threshold:.0%}")
    logger.info(f"  Use LLM: {use_llm}")
    logger.info(f"  Dry run: {dry_run}")
    logger.info("=" * 60)
    
    # 1. Ladda alla block
    blocks = load_all_blocks(lake_dir)
    if not blocks:
        logger.info("No blocks found.")
        return
    
    # 2. Beräkna embeddings
    blocks = compute_embeddings(blocks)
    
    # 3. Hitta duplikat
    duplicates = find_duplicates(blocks, threshold)
    
    if not duplicates:
        logger.info("No duplicates found!")
        return
    
    logger.info(f"Found {len(duplicates)} duplicate pairs")
    
    # 4. Merge duplikat (med LLM)
    kept, merged, removed = await deduplicate_blocks(blocks, duplicates, use_llm)
    
    # 5. Spara resultat
    save_results(lake_dir, kept, merged, removed, dry_run)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline 2.0 - Deduplicator (LLM-driven)")
    parser.add_argument('--threshold', type=float, default=0.85,
                       help='Similarity threshold for duplicates (default: 0.85)')
    parser.add_argument('--apply', action='store_true',
                       help='Actually apply changes (default: dry run)')
    parser.add_argument('--lake', type=str, default='storage/lake_v2',
                       help='Path to lake directory')
    parser.add_argument('--no-llm', action='store_true',
                       help='Disable LLM merge (use simple fallback)')
    args = parser.parse_args()
    
    lake_dir = AI_SERVICES_DIR / args.lake
    
    asyncio.run(run_deduplication(
        lake_dir=lake_dir,
        threshold=args.threshold,
        dry_run=not args.apply,
        use_llm=not args.no_llm
    ))


if __name__ == "__main__":
    main()
