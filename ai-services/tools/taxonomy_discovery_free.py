"""
Taxonomy Discovery Tool - Bottom-Up Analysis
Analyzes Smart Blocks in storage/lake/ and proposes a taxonomy without predefined categories.
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
log = logging.getLogger("TaxonomyDiscovery")

# --- TURBO MODE CONFIG (from start_pipeline.py) ---
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


# --- PYDANTIC MODEL: The Open Container ---
class Taxon(BaseModel):
    """AI response model for taxonomy classification."""
    granular_topics: List[str] = Field(
        ..., 
        description="Exakta ämnen/objekt i texten, ex: '320-timmarsregeln', 'Senior Konsult'"
    )
    proposed_branch: str = Field(
        ..., 
        description="Ett logiskt samlingsnamn för dessa ämnen, ex: 'Prismodeller' eller 'Rollbeskrivningar'"
    )
    proposed_root: str = Field(
        ..., 
        description="Den högsta abstrakta kategorin, ex: 'Affärsregler' eller 'Process'"
    )


# --- SYSTEM PROMPT: The Expert Taxonomist ---
TAXONOMIST_PROMPT = """Du är en expert på informationsarkitektur för offentlig IT-upphandling. 
Analysera följande textsegment.

1. Identifiera de mest specifika begreppen (Granular Topics) - exakta termer, regler, roller, belopp.
2. Gruppera dem i en logisk underkategori (Proposed Branch) - t.ex. "Prismodeller", "Rollbeskrivningar", "Avtalsvillkor".
3. Placera dem i en toppkategori (Proposed Root) - t.ex. "Affärsregler", "Process", "Kompetens", "Juridik".

Var konsekvent med namngivning där det är möjligt, men tvinga inte in data i fel kategori.

Svara ENDAST med valid JSON med EXAKT dessa tre nycklar:
{{
  "granular_topics": ["term1", "term2", ...],
  "proposed_branch": "Underkategori",
  "proposed_root": "Toppkategori"
}}

--- TEXTSEGMENT ---
{content}
"""


# --- ADAPTIVE THROTTLER (from start_pipeline.py) ---
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
            log.warning(f"🛑 429 DETECTED! Bromsar: {int(old_limit)} -> {int(self.limit)}. Paus {COOLDOWN_TIME}s.")
        await asyncio.sleep(COOLDOWN_TIME)


# --- TAXONOMY MAP: The Aggregator ---
class TaxonomyMap:
    """Aggregates taxonomy results from multiple files."""
    
    def __init__(self):
        # Structure: Root -> Branch -> {topics: Set, file_count: int, files: List}
        self.data: Dict[str, Dict[str, Dict]] = defaultdict(
            lambda: defaultdict(lambda: {"topics": set(), "file_count": 0, "files": []})
        )
        self.errors: List[Dict] = []
        self.processed_count = 0
    
    def add_result(self, filename: str, taxon: Taxon):
        """Add a taxonomy result to the map."""
        root = taxon.proposed_root
        branch = taxon.proposed_branch
        
        self.data[root][branch]["topics"].update(taxon.granular_topics)
        self.data[root][branch]["file_count"] += 1
        self.data[root][branch]["files"].append(filename)
        self.processed_count += 1
    
    def add_error(self, filename: str, error: str):
        """Track files that failed to process."""
        self.errors.append({"file": filename, "error": error})
    
    def to_dict(self) -> dict:
        """Convert to serializable dictionary."""
        result = {}
        for root, branches in self.data.items():
            result[root] = {}
            for branch, data in branches.items():
                result[root][branch] = {
                    "topics": sorted(list(data["topics"])),
                    "file_count": data["file_count"],
                    "files": data["files"]
                }
        return result
    
    def get_stats(self) -> str:
        """Generate statistics report sorted by frequency."""
        lines = []
        lines.append("=" * 60)
        lines.append("TAXONOMY DISCOVERY STATISTICS")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Total files processed: {self.processed_count}")
        lines.append(f"Errors: {len(self.errors)}")
        lines.append("=" * 60)
        lines.append("")
        
        # Root categories sorted by total file count
        root_counts = []
        for root, branches in self.data.items():
            total = sum(b["file_count"] for b in branches.values())
            root_counts.append((root, total, len(branches)))
        
        root_counts.sort(key=lambda x: -x[1])
        
        lines.append("TOP ROOT CATEGORIES (by file count):")
        lines.append("-" * 40)
        for root, count, branch_count in root_counts:
            lines.append(f"  {root}: {count} files, {branch_count} branches")
        
        lines.append("")
        lines.append("TOP BRANCHES (by file count):")
        lines.append("-" * 40)
        
        # All branches sorted by file count
        branch_list = []
        for root, branches in self.data.items():
            for branch, data in branches.items():
                branch_list.append((root, branch, data["file_count"], len(data["topics"])))
        
        branch_list.sort(key=lambda x: -x[2])
        
        for root, branch, file_count, topic_count in branch_list[:20]:
            lines.append(f"  [{root}] {branch}: {file_count} files, {topic_count} topics")
        
        lines.append("")
        lines.append("ALL TOPICS (unique):")
        lines.append("-" * 40)
        
        all_topics = set()
        for branches in self.data.values():
            for data in branches.values():
                all_topics.update(data["topics"])
        
        for topic in sorted(all_topics)[:50]:
            lines.append(f"  - {topic}")
        
        if len(all_topics) > 50:
            lines.append(f"  ... and {len(all_topics) - 50} more")
        
        if self.errors:
            lines.append("")
            lines.append("ERRORS:")
            lines.append("-" * 40)
            for err in self.errors[:10]:
                lines.append(f"  {err['file']}: {err['error'][:50]}...")
        
        return "\n".join(lines)


# --- FILE READER ---
def read_smart_block(file_path: Path) -> tuple[str, str]:
    """Read a Smart Block markdown file and extract content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body = parts[2].strip()
                return frontmatter_text, body
        
        return "", content
    except Exception as e:
        log.error(f"Error reading {file_path.name}: {e}")
        return "", ""


# --- AI ANALYZER ---
async def analyze_file(
    file_path: Path, 
    client: genai.Client, 
    model: str, 
    throttler: AdaptiveThrottler
) -> tuple[str, Taxon | None, str | None]:
    """Analyze a single file and return taxonomy classification."""
    filename = file_path.name
    frontmatter, body = read_smart_block(file_path)
    
    if not body or len(body.strip()) < 50:
        return filename, None, "Content too short"
    
    # Truncate very long content
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
                
                # Handle nested structure if LLM wraps in extra object
                if isinstance(data, dict):
                    # Check if it's wrapped in a container
                    if "taxon" in data:
                        data = data["taxon"]
                    elif "result" in data:
                        data = data["result"]
                
                # Validate required fields exist
                if not isinstance(data, dict):
                    return filename, None, f"Invalid response type: {type(data)}"
                
                # Map potential alternative field names
                mapped_data = {
                    "granular_topics": data.get("granular_topics") or data.get("topics") or data.get("granularTopics") or [],
                    "proposed_branch": data.get("proposed_branch") or data.get("branch") or data.get("proposedBranch") or "Unknown",
                    "proposed_root": data.get("proposed_root") or data.get("root") or data.get("proposedRoot") or "Unknown"
                }
                
                taxon = Taxon(**mapped_data)
                return filename, taxon, None
            except json.JSONDecodeError as json_err:
                return filename, None, f"JSON decode error: {json_err}"
            except Exception as parse_err:
                return filename, None, f"Parse error: {type(parse_err).__name__}: {str(parse_err)[:100]}"
                
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str:
                throttler.release()
                await throttler.brake()
                continue
            else:
                throttler.release()
                return filename, None, f"API error: {err_str[:100]}"


# --- MAIN ---
async def main():
    log.info("=" * 60)
    log.info("TAXONOMY DISCOVERY - Bottom-Up Analysis")
    log.info("=" * 60)
    
    # Load environment
    env_path = AI_SERVICES_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        log.error("GOOGLE_API_KEY saknas.")
        return
    
    # Load config for model name
    config_path = AI_SERVICES_DIR / "data_pipeline" / "config" / "pipeline_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    model = config['system']['models']['model_fast']  # Use fast model for analysis
    log.info(f"Using model: {model}")
    
    # Initialize
    client = genai.Client(api_key=api_key)
    throttler = AdaptiveThrottler(INITIAL_CONCURRENCY, MIN_CONCURRENCY, MAX_CONCURRENCY)
    taxonomy_map = TaxonomyMap()
    
    # Get all markdown files
    if not LAKE_DIR.exists():
        log.error(f"Lake directory not found: {LAKE_DIR}")
        return
    
    md_files = list(LAKE_DIR.glob("*.md"))
    log.info(f"Found {len(md_files)} markdown files in lake")
    
    # Process files with progress bar
    tasks = []
    for file_path in md_files:
        tasks.append(analyze_file(file_path, client, model, throttler))
    
    log.info(f"Starting analysis with Turbo Mode (concurrency: {INITIAL_CONCURRENCY}-{MAX_CONCURRENCY})")
    
    # Run with progress tracking
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
            taxonomy_map.add_result(filename, taxon)
        elif error:
            taxonomy_map.add_error(filename, error)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save emergent_taxonomy.json
    taxonomy_path = OUTPUT_DIR / "emergent_taxonomy.json"
    with open(taxonomy_path, 'w', encoding='utf-8') as f:
        json.dump(taxonomy_map.to_dict(), f, ensure_ascii=False, indent=2)
    log.info(f"Saved: {taxonomy_path}")
    
    # Save taxonomy_stats.txt
    stats_path = OUTPUT_DIR / "taxonomy_stats.txt"
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(taxonomy_map.get_stats())
    log.info(f"Saved: {stats_path}")
    
    # Print summary
    log.info("")
    log.info("=" * 60)
    log.info("SUMMARY")
    log.info("=" * 60)
    log.info(f"Files processed: {taxonomy_map.processed_count}")
    log.info(f"Errors: {len(taxonomy_map.errors)}")
    log.info(f"Root categories discovered: {len(taxonomy_map.data)}")
    
    total_branches = sum(len(b) for b in taxonomy_map.data.values())
    log.info(f"Branch categories discovered: {total_branches}")
    
    all_topics = set()
    for branches in taxonomy_map.data.values():
        for data in branches.values():
            all_topics.update(data["topics"])
    log.info(f"Unique topics discovered: {len(all_topics)}")
    
    log.info("")
    log.info(f"Results saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

