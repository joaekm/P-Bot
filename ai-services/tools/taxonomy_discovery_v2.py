"""
Taxonomy Discovery Tool v2 - Scope-Aware Analysis
Analyzes Smart Blocks with strict hierarchy and Scope Context dimension.
"""
import os
import json
import yaml
import asyncio
import time
import logging
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv
from tqdm import tqdm

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("TaxonomyDiscoveryV2")

# --- TURBO MODE CONFIG ---
INITIAL_CONCURRENCY = 5
MAX_CONCURRENCY = 50
MIN_CONCURRENCY = 1
GAS_STEP = 1.0
BRAKE_FACTOR = 0.5
COOLDOWN_TIME = 10

# --- PATHS ---
CURRENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CURRENT_DIR.parent.parent
AI_SERVICES_DIR = PROJECT_ROOT / "ai-services"
LAKE_DIR = AI_SERVICES_DIR / "storage" / "lake"
OUTPUT_DIR = AI_SERVICES_DIR / "tools" / "output"


# =============================================================================
# TAXONOMY ENUMS & PYDANTIC MODELS
# =============================================================================

class TaxonomyRoot(str, Enum):
    DOMAIN_OBJECTS = "DOMAIN_OBJECTS"       # Det fysiska/konkreta
    BUSINESS_CONCEPTS = "BUSINESS_CONCEPTS" # Det abstrakta/logiska
    PROCESS = "PROCESS"                     # Tiden/Flödet


class TaxonomyBranch(str, Enum):
    # Under DOMAIN_OBJECTS
    ROLES = "ROLES"             # Roller, Kompetens, Nivåer
    ARTIFACTS = "ARTIFACTS"     # CV, Avtal, Bilagor, Dokument
    LOCATIONS = "LOCATIONS"     # Regioner, Geografi, Plats
    
    # Under BUSINESS_CONCEPTS
    FINANCIALS = "FINANCIALS"   # Pris, Volym, Budget, Optioner
    GOVERNANCE = "GOVERNANCE"   # Lagar, Regler, Säkerhet, GDPR, Compliance
    STRATEGY = "STRATEGY"       # Affärsregler, Avropsformer (FKU/DR), Metod
    
    # Under PROCESS
    PHASES = "PHASES"           # Intake, Evaluation, Contract, Management


class ScopeContext(str, Enum):
    FRAMEWORK_SPECIFIC = "FRAMEWORK_SPECIFIC"  # Specifikt för Adda Ramavtal
    GENERAL_LEGAL = "GENERAL_LEGAL"            # Allmän lag/praxis
    DOMAIN_KNOWLEDGE = "DOMAIN_KNOWLEDGE"      # Allmän branschkunskap


# Valid branch mappings per root
VALID_BRANCHES = {
    TaxonomyRoot.DOMAIN_OBJECTS: [TaxonomyBranch.ROLES, TaxonomyBranch.ARTIFACTS, TaxonomyBranch.LOCATIONS],
    TaxonomyRoot.BUSINESS_CONCEPTS: [TaxonomyBranch.FINANCIALS, TaxonomyBranch.GOVERNANCE, TaxonomyBranch.STRATEGY],
    TaxonomyRoot.PROCESS: [TaxonomyBranch.PHASES],
}


class Taxon(BaseModel):
    """AI response model for scope-aware taxonomy classification."""
    root: TaxonomyRoot
    branch: TaxonomyBranch
    scope_context: ScopeContext = Field(
        ..., 
        description="Är detta en specifik regel för detta avtal, eller en allmän lag/fakta?"
    )
    granular_topics: List[str] = Field(
        ..., 
        description="KONCEPT bara (t.ex. 'Timpris'). INGA värden (t.ex. '1200 kr')!"
    )


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

TAXONOMIST_PROMPT = """Du är en expert på informationsarkitektur för offentlig IT-upphandling.
Analysera följande textsegment och klassificera det enligt den strikta taxonomin.

## TAXONOMI-STRUKTUR

**ROOT-kategorier:**
- DOMAIN_OBJECTS: Det fysiska/konkreta (roller, dokument, platser)
- BUSINESS_CONCEPTS: Det abstrakta/logiska (pris, regler, strategi)
- PROCESS: Tiden/Flödet (faser, steg)

**BRANCH per ROOT:**
- DOMAIN_OBJECTS → ROLES (roller, kompetens, nivåer), ARTIFACTS (CV, avtal, bilagor), LOCATIONS (regioner, geografi)
- BUSINESS_CONCEPTS → FINANCIALS (pris, volym, budget), GOVERNANCE (lagar, regler, GDPR), STRATEGY (avropsformer, affärsregler)
- PROCESS → PHASES (intake, evaluation, contract, management)

## SCOPE CONTEXT (KRITISKT!)

Du MÅSTE avgöra räckvidden:
- **FRAMEWORK_SPECIFIC**: Specifika regler för Adda Ramavtal (t.ex. "320-timmarsregeln", "KN5-regeln", specifika pristak, specifika roller i avtalet)
- **GENERAL_LEGAL**: Allmänna lagar och praxis (t.ex. LOU, GDPR, Sekretesslagen, Upphandlingsregler)
- **DOMAIN_KNOWLEDGE**: Allmän branschkunskap (t.ex. "Vad gör en Javautvecklare?", "Vad är agil metodik?")

## ANTI-POLLUTION (KRITISKT!)

EXTRAHERA INTE VÄRDEN! Endast koncept/begrepp.
- ❌ FEL: "1200 kr", "2024-01-01", "10 MSEK", "5 år"
- ✅ RÄTT: "Takpris", "Avtalsstart", "Maxbelopp", "Avtalstid"

Om texten säger "Takpris är 1200 kr" → topic = "Takpris"
Om texten säger "Gäller från 2024-01-01" → topic = "Avtalsstart"
Om texten säger "Minst 5 års erfarenhet" → topic = "Erfarenhetskrav"

## OUTPUT FORMAT

Svara ENDAST med valid JSON:
{{
  "root": "DOMAIN_OBJECTS" | "BUSINESS_CONCEPTS" | "PROCESS",
  "branch": "ROLES" | "ARTIFACTS" | "LOCATIONS" | "FINANCIALS" | "GOVERNANCE" | "STRATEGY" | "PHASES",
  "scope_context": "FRAMEWORK_SPECIFIC" | "GENERAL_LEGAL" | "DOMAIN_KNOWLEDGE",
  "granular_topics": ["Koncept1", "Koncept2", ...]
}}

--- TEXTSEGMENT ---
{content}
"""


# =============================================================================
# ADAPTIVE THROTTLER
# =============================================================================

class AdaptiveThrottler:
    def __init__(self, start, min_limit, max_limit):
        self.limit = float(start)
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.current_running = 0
        self.lock = asyncio.Lock()
        self.last_brake = 0

    async def wait_for_slot(self):
        while True:
            async with self.lock:
                if self.current_running < int(self.limit):
                    self.current_running += 1
                    return
            await asyncio.sleep(0.1)

    def release(self):
        self.current_running -= 1

    async def gas(self):
        async with self.lock:
            if self.limit < self.max_limit:
                self.limit += GAS_STEP

    async def brake(self):
        async with self.lock:
            now = time.time()
            if now - self.last_brake < 2.0: 
                return 
            self.last_brake = now
            old_limit = self.limit
            self.limit = max(self.min_limit, self.limit * BRAKE_FACTOR)
            log.warning(f"429 DETECTED! Throttle: {int(old_limit)} -> {int(self.limit)}. Pause {COOLDOWN_TIME}s.")
        await asyncio.sleep(COOLDOWN_TIME)


# =============================================================================
# TAXONOMY AGGREGATOR
# =============================================================================

class TaxonomyAggregator:
    """Aggregates taxonomy results with scope awareness."""
    
    def __init__(self):
        # Structure: Root -> Branch -> Scope -> {topics, count, files}
        self.data: Dict = {}
        for root in TaxonomyRoot:
            self.data[root.value] = {}
            for branch in VALID_BRANCHES.get(root, []):
                self.data[root.value][branch.value] = {}
                for scope in ScopeContext:
                    self.data[root.value][branch.value][scope.value] = {
                        "count": 0,
                        "topics": set(),
                        "files": []
                    }
        
        self.errors: List[Dict] = []
        self.processed_count = 0
        self.validation_errors = 0
    
    def add_result(self, filename: str, taxon: Taxon):
        """Add a taxonomy result to the aggregator."""
        root = taxon.root.value
        branch = taxon.branch.value
        scope = taxon.scope_context.value
        
        # Validate branch belongs to root
        if taxon.branch not in VALID_BRANCHES.get(taxon.root, []):
            self.validation_errors += 1
            # Fall back to first valid branch for this root
            valid_branches = VALID_BRANCHES.get(taxon.root, [])
            if valid_branches:
                branch = valid_branches[0].value
            else:
                self.add_error(filename, f"Invalid root-branch combo: {root}/{branch}")
                return
        
        self.data[root][branch][scope]["count"] += 1
        self.data[root][branch][scope]["topics"].update(taxon.granular_topics)
        self.data[root][branch][scope]["files"].append(filename)
        self.processed_count += 1
    
    def add_error(self, filename: str, error: str):
        """Track files that failed to process."""
        self.errors.append({"file": filename, "error": error})
    
    def to_dict(self) -> dict:
        """Convert to serializable dictionary."""
        result = {}
        for root, branches in self.data.items():
            result[root] = {}
            for branch, scopes in branches.items():
                result[root][branch] = {}
                for scope, data in scopes.items():
                    if data["count"] > 0:  # Only include non-empty
                        result[root][branch][scope] = {
                            "count": data["count"],
                            "topics": sorted(list(data["topics"])),
                            "files": data["files"]
                        }
                # Remove empty branches
                if not result[root][branch]:
                    del result[root][branch]
            # Remove empty roots
            if not result[root]:
                del result[root]
        return result
    
    def get_stats(self) -> str:
        """Generate statistics report with scope distribution."""
        lines = []
        lines.append("=" * 70)
        lines.append("TAXONOMY DISCOVERY v2 - SCOPE-AWARE ANALYSIS")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Total files processed: {self.processed_count}")
        lines.append(f"Validation corrections: {self.validation_errors}")
        lines.append(f"Errors: {len(self.errors)}")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary by Root
        lines.append("DISTRIBUTION BY ROOT CATEGORY:")
        lines.append("-" * 50)
        for root in TaxonomyRoot:
            total = sum(
                self.data[root.value][b.value][s.value]["count"]
                for b in VALID_BRANCHES.get(root, [])
                for s in ScopeContext
            )
            lines.append(f"  {root.value}: {total} files")
        
        lines.append("")
        lines.append("DISTRIBUTION BY BRANCH + SCOPE:")
        lines.append("-" * 50)
        
        # Detailed breakdown
        for root in TaxonomyRoot:
            lines.append(f"\n[{root.value}]")
            for branch in VALID_BRANCHES.get(root, []):
                branch_total = sum(
                    self.data[root.value][branch.value][s.value]["count"]
                    for s in ScopeContext
                )
                if branch_total == 0:
                    continue
                
                lines.append(f"  {branch.value}: {branch_total} total")
                for scope in ScopeContext:
                    count = self.data[root.value][branch.value][scope.value]["count"]
                    topics = self.data[root.value][branch.value][scope.value]["topics"]
                    if count > 0:
                        lines.append(f"    - {scope.value}: {count} files, {len(topics)} topics")
        
        # Scope distribution summary
        lines.append("")
        lines.append("=" * 70)
        lines.append("SCOPE CONTEXT SUMMARY (Critical for Strategy)")
        lines.append("=" * 70)
        
        scope_totals = {s.value: 0 for s in ScopeContext}
        for root in TaxonomyRoot:
            for branch in VALID_BRANCHES.get(root, []):
                for scope in ScopeContext:
                    scope_totals[scope.value] += self.data[root.value][branch.value][scope.value]["count"]
        
        total_files = sum(scope_totals.values())
        for scope, count in sorted(scope_totals.items(), key=lambda x: -x[1]):
            pct = (count / total_files * 100) if total_files > 0 else 0
            bar = "█" * int(pct / 2)
            lines.append(f"  {scope}: {count} files ({pct:.1f}%) {bar}")
        
        # Top topics per scope
        lines.append("")
        lines.append("TOP TOPICS BY SCOPE:")
        lines.append("-" * 50)
        
        for scope in ScopeContext:
            all_topics = set()
            for root in TaxonomyRoot:
                for branch in VALID_BRANCHES.get(root, []):
                    all_topics.update(self.data[root.value][branch.value][scope.value]["topics"])
            
            if all_topics:
                lines.append(f"\n[{scope.value}] ({len(all_topics)} unique topics)")
                for topic in sorted(list(all_topics))[:15]:
                    lines.append(f"    - {topic}")
                if len(all_topics) > 15:
                    lines.append(f"    ... and {len(all_topics) - 15} more")
        
        # Errors
        if self.errors:
            lines.append("")
            lines.append("ERRORS:")
            lines.append("-" * 50)
            for err in self.errors[:10]:
                lines.append(f"  {err['file']}: {err['error'][:60]}...")
            if len(self.errors) > 10:
                lines.append(f"  ... and {len(self.errors) - 10} more errors")
        
        return "\n".join(lines)


# =============================================================================
# FILE READER
# =============================================================================

def read_smart_block(file_path: Path) -> tuple[str, str]:
    """Read a Smart Block markdown file and extract content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[1], parts[2].strip()
        
        return "", content
    except Exception as e:
        log.error(f"Error reading {file_path.name}: {e}")
        return "", ""


# =============================================================================
# AI ANALYZER
# =============================================================================

async def analyze_file(
    file_path: Path, 
    client: genai.Client, 
    model: str, 
    throttler: AdaptiveThrottler
) -> tuple[str, Taxon | None, str | None]:
    """Analyze a single file and return scope-aware taxonomy classification."""
    filename = file_path.name
    frontmatter, body = read_smart_block(file_path)
    
    if not body or len(body.strip()) < 50:
        return filename, None, "Content too short"
    
    content = body[:4000] if len(body) > 4000 else body
    prompt = TAXONOMIST_PROMPT.format(content=content)
    
    while True:
        await throttler.wait_for_slot()
        try:
            response = await client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            await throttler.gas()
            throttler.release()
            
            # Parse response
            try:
                raw_text = response.text.strip()
                data = json.loads(raw_text)
                
                # Map string values to enums
                mapped_data = {
                    "root": data.get("root", "DOMAIN_OBJECTS"),
                    "branch": data.get("branch", "ROLES"),
                    "scope_context": data.get("scope_context", "FRAMEWORK_SPECIFIC"),
                    "granular_topics": data.get("granular_topics", [])
                }
                
                # Filter out value-like topics (numbers, dates, prices)
                filtered_topics = []
                for topic in mapped_data["granular_topics"]:
                    topic_str = str(topic).strip()
                    # Skip if it looks like a value
                    if any(c.isdigit() for c in topic_str) and len(topic_str) < 20:
                        # Allow if it's a concept with a number (e.g., "Nivå 5")
                        if not any(kw in topic_str.lower() for kw in ["nivå", "steg", "fas", "version"]):
                            continue
                    if topic_str.startswith("20") and "-" in topic_str:  # Date
                        continue
                    if "SEK" in topic_str or "kr" in topic_str.lower():  # Price
                        continue
                    if topic_str:
                        filtered_topics.append(topic_str)
                
                mapped_data["granular_topics"] = filtered_topics
                
                taxon = Taxon(**mapped_data)
                return filename, taxon, None
                
            except json.JSONDecodeError as json_err:
                return filename, None, f"JSON decode error: {json_err}"
            except Exception as parse_err:
                return filename, None, f"Parse error: {type(parse_err).__name__}: {str(parse_err)[:80]}"
                
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                throttler.release()
                await throttler.brake()
                continue
            else:
                throttler.release()
                return filename, None, f"API error: {err_str[:100]}"


# =============================================================================
# MAIN
# =============================================================================

async def main():
    log.info("=" * 70)
    log.info("TAXONOMY DISCOVERY v2 - Scope-Aware Analysis")
    log.info("=" * 70)
    
    # Load environment
    env_path = AI_SERVICES_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.error("GOOGLE_API_KEY missing.")
        return
    
    # Load config
    config_path = AI_SERVICES_DIR / "data_pipeline" / "config" / "pipeline_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    model = config['system']['models']['model_fast']
    log.info(f"Using model: {model}")
    
    # Initialize
    client = genai.Client(api_key=api_key)
    throttler = AdaptiveThrottler(INITIAL_CONCURRENCY, MIN_CONCURRENCY, MAX_CONCURRENCY)
    aggregator = TaxonomyAggregator()
    
    # Get markdown files
    if not LAKE_DIR.exists():
        log.error(f"Lake directory not found: {LAKE_DIR}")
        return
    
    md_files = list(LAKE_DIR.glob("*.md"))
    log.info(f"Found {len(md_files)} markdown files in lake")
    
    # Process files
    tasks = [analyze_file(fp, client, model, throttler) for fp in md_files]
    
    log.info(f"Starting analysis with Turbo Mode (concurrency: {INITIAL_CONCURRENCY}-{MAX_CONCURRENCY})")
    
    results = []
    with tqdm(total=len(tasks), desc="Analyzing files", unit="file") as pbar:
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            pbar.update(1)
            pbar.set_postfix({"concurrency": int(throttler.limit)})
    
    # Aggregate results
    log.info("Aggregating results...")
    for filename, taxon, error in results:
        if taxon:
            aggregator.add_result(filename, taxon)
        elif error:
            aggregator.add_error(filename, error)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_path = OUTPUT_DIR / "taxonomy_v2_scope_test.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(aggregator.to_dict(), f, ensure_ascii=False, indent=2)
    log.info(f"Saved: {json_path}")
    
    # Save stats
    stats_path = OUTPUT_DIR / "taxonomy_v2_stats.txt"
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(aggregator.get_stats())
    log.info(f"Saved: {stats_path}")
    
    # Print summary
    log.info("")
    log.info("=" * 70)
    log.info("SUMMARY")
    log.info("=" * 70)
    log.info(f"Files processed: {aggregator.processed_count}")
    log.info(f"Validation corrections: {aggregator.validation_errors}")
    log.info(f"Errors: {len(aggregator.errors)}")
    
    # Scope distribution
    scope_totals = {s.value: 0 for s in ScopeContext}
    for root in TaxonomyRoot:
        for branch in VALID_BRANCHES.get(root, []):
            for scope in ScopeContext:
                scope_totals[scope.value] += aggregator.data[root.value][branch.value][scope.value]["count"]
    
    log.info("")
    log.info("SCOPE DISTRIBUTION:")
    for scope, count in sorted(scope_totals.items(), key=lambda x: -x[1]):
        log.info(f"  {scope}: {count} files")
    
    log.info("")
    log.info(f"Results saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

