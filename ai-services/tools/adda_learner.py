"""
Adda Learning Agent - One-Time Graph Enrichment

Analyzes Smart Blocks from data_pipeline/output/ and extracts relations
for building a rich knowledge graph. This is a ONE-TIME batch process.

Learning Types:
- geo: City -> County (from kommun-kopplingar document)
- roles: Exempelroll -> Kompetensomrade (from Bilaga A)
- rules: Affarsregler och triggers
- aliases: Namnvarianter och synonymer

Usage:
    python tools/adda_learner.py --output config/learnings.json

Output:
    JSON file with extracted learnings to be applied by adda_indexer.py
"""
import os
import json
import yaml
import asyncio
import logging
import uuid
import re
import time
from pathlib import Path
from typing import List, Dict, Optional, Set
from datetime import datetime

from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tqdm import tqdm
import argparse

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("AddaLearner")

# --- TURBO MODE CONFIG ---
INITIAL_CONCURRENCY = 5
MAX_CONCURRENCY = 50
MIN_CONCURRENCY = 1
GAS_STEP = 1.0
BRAKE_FACTOR = 0.5
COOLDOWN_TIME = 10

# --- PATHS ---
CURRENT_DIR = Path(__file__).parent.resolve()
AI_SERVICES_DIR = CURRENT_DIR.parent
# Default: Read from storage/lake (populated manually from data_pipeline/output)
OUTPUT_DIR = AI_SERVICES_DIR / "storage" / "lake"
CONFIG_DIR = AI_SERVICES_DIR / "config"
TAXONOMY_PATH = CONFIG_DIR / "adda_taxonomy.json"

# --- LOAD ENV ---
load_dotenv(AI_SERVICES_DIR / ".env")

# --- GEMINI CONFIG ---
GEMINI_MODEL = "gemini-2.0-flash"  # Fast model for analysis


# =============================================================================
# ADAPTIVE THROTTLER (Turbo Mode)
# =============================================================================

class AdaptiveThrottler:
    """
    Adaptive rate limiter that speeds up on success and slows down on 429 errors.
    Same pattern as start_pipeline.py.
    """
    def __init__(self, start: int, min_limit: int, max_limit: int):
        self.limit = float(start)
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.current_running = 0
        self.lock = asyncio.Lock()
        self.last_brake = 0

    async def wait_for_slot(self):
        """Wait until a slot is available."""
        while True:
            async with self.lock:
                if self.current_running < int(self.limit):
                    self.current_running += 1
                    return
            await asyncio.sleep(0.1)

    def release(self):
        """Release a slot."""
        self.current_running -= 1

    async def gas(self):
        """Increase concurrency on success."""
        async with self.lock:
            if self.limit < self.max_limit:
                self.limit += GAS_STEP

    async def brake(self):
        """Decrease concurrency on 429 error."""
        async with self.lock:
            now = time.time()
            if now - self.last_brake < 2.0:
                return
            self.last_brake = now
            old_limit = self.limit
            self.limit = max(self.min_limit, self.limit * BRAKE_FACTOR)
            log.warning(f"🛑 429 DETECTED! Throttle: {int(old_limit)} -> {int(self.limit)}. Pause {COOLDOWN_TIME}s.")
        await asyncio.sleep(COOLDOWN_TIME)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class GeoLearning(BaseModel):
    """Geographic relation: City -> County"""
    city: str = Field(..., description="Namn på stad/kommun")
    county: str = Field(..., description="Namn på län (utan 'län' suffix)")


class RoleLearning(BaseModel):
    """Role relation: Exempelroll -> Kompetensomrade"""
    role: str = Field(..., description="Namn på exempelroll")
    kompetensomrade: str = Field(..., description="Kompetensområde rollen tillhör")


class RuleLearning(BaseModel):
    """Business rule extraction"""
    subject: str = Field(..., description="Vad regeln gäller")
    predicate: str = Field(..., description="Relation (t.ex. 'kräver', 'begränsar')")
    object: str = Field(..., description="Konsekvens/mål")


class AliasLearning(BaseModel):
    """Alias/synonym detection"""
    alias: str = Field(..., description="Alternativt namn/felstavning")
    canonical: str = Field(..., description="Korrekt/kanoniskt namn")
    entity_type: str = Field(..., description="Typ: Roll, Plats, Begrepp")


class DocumentLearnings(BaseModel):
    """All learnings extracted from a document"""
    geo: List[GeoLearning] = Field(default_factory=list)
    roles: List[RoleLearning] = Field(default_factory=list)
    rules: List[RuleLearning] = Field(default_factory=list)
    aliases: List[AliasLearning] = Field(default_factory=list)


# =============================================================================
# TAXONOMY LOADER
# =============================================================================

def load_taxonomy() -> Dict:
    """Load master taxonomy for reference."""
    if not TAXONOMY_PATH.exists():
        log.warning(f"Taxonomy not found at {TAXONOMY_PATH}")
        return {}
    
    with open(TAXONOMY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# GEMINI CLIENT
# =============================================================================

def init_gemini():
    """Initialize Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY in .env")
    
    client = genai.Client(api_key=api_key)
    return client


async def analyze_document_with_llm(
    client: genai.Client,
    content: str,
    taxonomy: Dict,
    filename: str,
    throttler: AdaptiveThrottler
) -> DocumentLearnings:
    """
    Analyze a document with LLM and extract learnings.
    Uses structured output for reliable extraction.
    Uses AdaptiveThrottler for rate limiting (Turbo Mode).
    """
    # Build reference lists from taxonomy
    areas = list(taxonomy.get("anbudsomraden", {}).get("areas", {}).keys())
    counties = []
    for area_info in taxonomy.get("anbudsomraden", {}).get("areas", {}).values():
        counties.extend(area_info.get("counties", []))
    
    kompetensomraden = taxonomy.get("kompetensomraden", {}).get("areas", [])
    
    prompt = f"""
Analysera följande dokument från Adda IT-konsulttjänster 2021 ramavtalet.

TAXONOMI-REFERENS (MASTER):
- Anbudsområden: {', '.join(areas)}
- Län: {', '.join(counties)}
- Kompetensområden: {', '.join(kompetensomraden)}

DOKUMENT ({filename}):
---
{content[:15000]}
---

EXTRAHERA följande typer av lärdomar:

1. GEO (Geografiska kopplingar):
   - Hitta städer/kommuner och deras län
   - Exempel: "Härnösand" -> "Västernorrland"
   - VIKTIGT: Använd länsnamn utan "län" suffix

2. ROLES (Rollkopplingar):
   - Hitta exempelroller och deras kompetensområde
   - Använd ENDAST kompetensområden från TAXONOMI-REFERENS
   - Exempel: "Fullstackutvecklare" -> "Systemutveckling"

3. RULES (Affärsregler):
   - Hitta explicita regler, triggers, begränsningar
   - Exempel: "Nivå 5" kräver "FKU"
   - Exempel: "Volym > 320h" begränsar "DR"

4. ALIASES (Synonymer/varianter):
   - Hitta alternativa namn, förkortningar, vanliga felstavningar
   - Exempel: "FKU" är alias för "Förnyad Konkurrensutsättning"
   - Exempel: "KN5" är alias för "Kompetensnivå 5"

Svara endast med de lärdomar du hittar i dokumentet.
Var konservativ - bättre att missa något än att gissa fel.
"""

    while True:
        await throttler.wait_for_slot()
        try:
            response = await client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=DocumentLearnings,
                    temperature=0.1  # Low temperature for factual extraction
                )
            )
            await throttler.gas()
            throttler.release()
            
            # Parse response
            if response.text:
                return DocumentLearnings.model_validate_json(response.text)
            return DocumentLearnings()
            
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                throttler.release()
                await throttler.brake()
                continue  # Retry
            else:
                throttler.release()
                log.warning(f"LLM analysis failed for {filename}: {e}")
                return DocumentLearnings()


# =============================================================================
# CSV PARSER (Deterministic geo extraction)
# =============================================================================

def extract_geo_from_csv(csv_path: Path, taxonomy: Dict) -> List[Dict]:
    """
    Extract city -> county mappings from SCB kommun-kopplingar CSV.
    This is deterministic (no LLM needed) for reliable geo data.
    """
    learnings = []
    valid_counties = set()
    
    # Get valid counties from taxonomy
    for area_info in taxonomy.get("anbudsomraden", {}).get("areas", {}).values():
        for county in area_info.get("counties", []):
            valid_counties.add(county.lower())
    
    if not csv_path.exists():
        log.warning(f"CSV file not found: {csv_path}")
        return learnings
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parse CSV (skip header rows)
    for line in lines[13:]:  # Data starts at line 14 (0-indexed: 13)
        parts = line.strip().split(',')
        if len(parts) >= 4:
            county_name = parts[1].strip()
            city_name = parts[3].strip()
            
            if city_name and county_name:
                # Normalize county name (taxonomy uses short form without "län")
                normalized_county = county_name
                
                learnings.append({
                    "type": "geo",
                    "subject": city_name,
                    "predicate": "located_in",
                    "object": normalized_county,
                    "confidence": 1.0  # Deterministic from official SCB data
                })
    
    log.info(f"Extracted {len(learnings)} geo learnings from CSV")
    return learnings


# =============================================================================
# DOCUMENT PROCESSOR
# =============================================================================

async def process_single_document(
    client: genai.Client,
    md_file: Path,
    taxonomy: Dict,
    throttler: AdaptiveThrottler
) -> List[Dict]:
    """Process a single document and return learnings."""
    learnings = []
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip small files
    if len(content) < 100:
        return learnings
    
    # Analyze with LLM (throttler handles rate limiting)
    doc_learnings = await analyze_document_with_llm(
        client, content, taxonomy, md_file.name, throttler
    )
    
    # Convert to flat format
    for geo in doc_learnings.geo:
        learnings.append({
            "type": "geo",
            "subject": geo.city,
            "predicate": "located_in",
            "object": geo.county,
            "confidence": 0.85,
            "source": md_file.name
        })
    
    for role in doc_learnings.roles:
        learnings.append({
            "type": "roles",
            "subject": role.role,
            "predicate": "belongs_to",
            "object": role.kompetensomrade,
            "confidence": 0.85,
            "source": md_file.name
        })
    
    for rule in doc_learnings.rules:
        learnings.append({
            "type": "rules",
            "subject": rule.subject,
            "predicate": rule.predicate,
            "object": rule.object,
            "confidence": 0.8,
            "source": md_file.name
        })
    
    for alias in doc_learnings.aliases:
        learnings.append({
            "type": "aliases",
            "alias": alias.alias,
            "canonical": alias.canonical,
            "entity_type": alias.entity_type,
            "confidence": 0.75,
            "source": md_file.name
        })
    
    return learnings


async def process_documents(
    client: genai.Client,
    taxonomy: Dict,
    output_dir: Path
) -> List[Dict]:
    """Process all documents in output directory with Turbo Mode."""
    all_learnings = []
    
    # Get all markdown files
    md_files = list(output_dir.glob("*.md"))
    log.info(f"Found {len(md_files)} documents to analyze")
    
    # Initialize throttler
    throttler = AdaptiveThrottler(INITIAL_CONCURRENCY, MIN_CONCURRENCY, MAX_CONCURRENCY)
    log.info(f"🚀 Starting Turbo Mode (concurrency: {INITIAL_CONCURRENCY}-{MAX_CONCURRENCY})")
    
    # Create tasks for all documents
    async def process_with_progress(md_file: Path, pbar) -> List[Dict]:
        result = await process_single_document(client, md_file, taxonomy, throttler)
        pbar.update(1)
        pbar.set_postfix({"active": throttler.current_running, "limit": int(throttler.limit)})
        return result
    
    # Process with progress bar
    with tqdm(total=len(md_files), desc="Analyzing documents") as pbar:
        tasks = [process_with_progress(md_file, pbar) for md_file in md_files]
        results = await asyncio.gather(*tasks)
    
    # Flatten results
    for doc_learnings in results:
        all_learnings.extend(doc_learnings)
    
    return all_learnings


def deduplicate_learnings(learnings: List[Dict]) -> List[Dict]:
    """Remove duplicate learnings, keeping highest confidence."""
    seen = {}
    
    for learning in learnings:
        ltype = learning.get("type", "")
        
        if ltype == "geo":
            key = (ltype, learning.get("subject", "").lower())
        elif ltype == "roles":
            key = (ltype, learning.get("subject", "").lower())
        elif ltype == "rules":
            key = (ltype, learning.get("subject", "").lower(), learning.get("object", "").lower())
        elif ltype == "aliases":
            key = (ltype, learning.get("alias", "").lower())
        else:
            key = (ltype, str(learning))
        
        if key not in seen or learning.get("confidence", 0) > seen[key].get("confidence", 0):
            seen[key] = learning
    
    return list(seen.values())


# =============================================================================
# MAIN
# =============================================================================

async def run_learning_pass(output_path: Path):
    """Run the complete learning pass."""
    log.info("=" * 60)
    log.info("ADDA LEARNING AGENT - One-Time Graph Enrichment")
    log.info("=" * 60)
    
    # Load taxonomy
    taxonomy = load_taxonomy()
    log.info(f"Loaded taxonomy from {TAXONOMY_PATH}")
    
    # Initialize Gemini
    client = init_gemini()
    log.info("Initialized Gemini client")
    
    all_learnings = []
    
    # 1. Extract geo from CSV (deterministic)
    csv_files = list((AI_SERVICES_DIR / "data_pipeline" / "input" / "primary").glob("*.csv"))
    for csv_file in csv_files:
        if "kommun" in csv_file.name.lower() or "kn" in csv_file.name.lower():
            log.info(f"Processing geo CSV: {csv_file.name}")
            geo_learnings = extract_geo_from_csv(csv_file, taxonomy)
            all_learnings.extend(geo_learnings)
    
    # 2. Process documents with LLM for roles, rules, aliases
    doc_learnings = await process_documents(client, taxonomy, OUTPUT_DIR)
    all_learnings.extend(doc_learnings)
    
    # 3. Deduplicate
    all_learnings = deduplicate_learnings(all_learnings)
    
    # 4. Summary
    geo_count = len([l for l in all_learnings if l.get("type") == "geo"])
    role_count = len([l for l in all_learnings if l.get("type") == "roles"])
    rule_count = len([l for l in all_learnings if l.get("type") == "rules"])
    alias_count = len([l for l in all_learnings if l.get("type") == "aliases"])
    
    log.info("=" * 60)
    log.info(f"LEARNING COMPLETE")
    log.info(f"  - Geo learnings: {geo_count}")
    log.info(f"  - Role learnings: {role_count}")
    log.info(f"  - Rule learnings: {rule_count}")
    log.info(f"  - Alias learnings: {alias_count}")
    log.info(f"  - Total: {len(all_learnings)}")
    
    # 5. Save to JSON
    output_data = {
        "version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "learnings": all_learnings
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    log.info(f"Saved learnings to {output_path}")
    log.info("=" * 60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Adda Learning Agent - One-Time Graph Enrichment"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="config/learnings.json",
        help="Output path for learnings JSON"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input directory (defaults to data_pipeline/output)"
    )
    
    args = parser.parse_args()
    
    # Resolve output path
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = AI_SERVICES_DIR / args.output
    
    # Override input dir if specified
    global OUTPUT_DIR
    if args.input:
        OUTPUT_DIR = Path(args.input)
        if not OUTPUT_DIR.is_absolute():
            OUTPUT_DIR = AI_SERVICES_DIR / args.input
    
    # Run async
    asyncio.run(run_learning_pass(output_path))


if __name__ == "__main__":
    main()

