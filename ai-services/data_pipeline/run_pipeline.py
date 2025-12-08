"""
Pipeline 2.0 - Orchestrator (Per-Avrop Flow)

Kör Pipeline 2.0 per avrop-fil:
1. Extractor: Extrahera frågor från ETT avrop
2. Tester: Testa frågor mot P-Bot + Judge
3. Creator: Skapa nya blocks för GAPs
4. Dedup: Städa duplikat med LLM-merge

Fördelar:
- Inga duplikat-kluster växer under körningen
- P-Bot har alltid ren kunskapsbas
- Catch problems early
"""

import os
import sys
import json
import yaml
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / 'logs' / f'pipeline_{datetime.now():%Y%m%d_%H%M%S}.log')
    ]
)
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
AI_SERVICES_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config" / "pipeline_v2_config.yaml"

# Ensure directories exist
(SCRIPT_DIR / 'logs').mkdir(exist_ok=True)
(SCRIPT_DIR / 'output').mkdir(exist_ok=True)


@dataclass
class PipelineStats:
    """Statistik för hela körningen."""
    started_at: str
    avrop_processed: int = 0
    total_questions: int = 0
    total_ok: int = 0
    total_improve: int = 0
    total_gap: int = 0
    total_blocks_created: int = 0
    dedup_runs: int = 0
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)


def load_config() -> Dict:
    """Ladda pipeline config."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_avrop_files(secondary_dir: Path, max_files: Optional[int] = None) -> List[Path]:
    """Hämta lista över avrop-filer att processa."""
    files = list(secondary_dir.glob('*'))
    files = [f for f in files if f.is_file() and f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
    files = sorted(files, key=lambda f: f.name)
    
    if max_files:
        files = files[:max_files]
    
    return files


async def process_single_avrop(
    avrop_file: Path,
    config: Dict,
    lake_dir: Path,
    index_dir: Path,
    stats: PipelineStats
) -> Dict:
    """
    Processa ETT avrop genom hela flödet:
    1. Extract questions
    2. Test against P-Bot
    3. Create blocks for GAPs
    4. Run dedup
    """
    from google import genai
    
    logger.info("=" * 60)
    logger.info(f"PROCESSING: {avrop_file.name}")
    logger.info("=" * 60)
    
    # Setup client
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")
    
    client = genai.Client(api_key=api_key)
    model_name = config.get('models', {}).get('extractor', 'gemini-2.0-flash')
    
    # --- STEP 1: EXTRACT ---
    logger.info(f"[1/4] Extracting questions from {avrop_file.name}...")
    
    from .extractor import read_document, extract_questions_from_avrop
    
    text = read_document(avrop_file)
    if not text:
        logger.warning(f"Could not read {avrop_file.name}, skipping")
        return {"questions": 0, "ok": 0, "improve": 0, "gap": 0, "blocks": 0}
    
    analysis = await extract_questions_from_avrop(
        client=client,
        avrop_text=text,
        avrop_id=avrop_file.stem,
        config=config,
        model_name=model_name
    )
    
    questions = analysis.questions
    logger.info(f"  → Extracted {len(questions)} questions")
    
    if not questions:
        return {"questions": 0, "ok": 0, "improve": 0, "gap": 0, "blocks": 0}
    
    # --- STEP 2: TEST ---
    logger.info(f"[2/4] Testing {len(questions)} questions against P-Bot...")
    
    from .tester import test_question, Verdict
    
    test_results = []
    ok_count = 0
    improve_count = 0
    gap_count = 0
    
    for i, q in enumerate(questions):
        # Skapa question_data dict som test_question förväntar sig
        question_data = {
            "question": q.question,
            "phase": q.phase,
            "anonymized_example": q.anonymized_example,
            "source_avrop_id": q.source_avrop_id,
            "decision_type": q.decision_type
        }
        
        result = await test_question(
            question_data=question_data,
            client=client,
            config=config,
            lake_dir=lake_dir
        )
        
        test_results.append({
            "question": q.question,
            "phase": q.phase,
            "verdict": result.verdict.value,
            "reasoning": result.judge_reasoning,
            "bot_response": result.bot_response,
            "sources_used": result.sources
        })
        
        if result.verdict == Verdict.OK:
            ok_count += 1
        elif result.verdict == Verdict.IMPROVE:
            improve_count += 1
        elif result.verdict == Verdict.GAP:
            gap_count += 1
        
        # Progress log every 5 questions
        if (i + 1) % 5 == 0:
            logger.info(f"  → Tested {i+1}/{len(questions)} (OK:{ok_count} IMPROVE:{improve_count} GAP:{gap_count})")
    
    logger.info(f"  → Results: OK={ok_count}, IMPROVE={improve_count}, GAP={gap_count}")
    
    # --- STEP 3: CREATE BLOCKS FOR GAPS ---
    blocks_created = 0
    
    if gap_count > 0:
        logger.info(f"[3/4] Creating blocks for {gap_count} GAPs...")
        
        from .creator import create_blocks_for_gap, load_document_registry
        
        registry = load_document_registry()
        
        gap_results = [r for r in test_results if r["verdict"] == "GAP"]
        
        for gap in gap_results:
            try:
                blocks = await create_blocks_for_gap(
                    gap_result=gap,
                    config=config,
                    registry=registry,
                    lake_dir=AI_SERVICES_DIR / config['paths'].get('primary_fulldocs', 'storage/lake'),
                    output_dir=lake_dir,
                    index_dir=index_dir
                )
                blocks_created += len(blocks) if blocks else 0
            except Exception as e:
                logger.error(f"  Error creating block: {e}")
        
        logger.info(f"  → Created {blocks_created} new blocks")
    else:
        logger.info("[3/4] No GAPs to process")
    
    # --- STEP 4: DEDUP ---
    logger.info("[4/4] Running deduplication...")
    
    from .deduplicator import run_deduplication
    
    await run_deduplication(
        lake_dir=lake_dir,
        threshold=0.85,
        dry_run=False,
        use_llm=True
    )
    
    stats.dedup_runs += 1
    
    # Update stats
    stats.avrop_processed += 1
    stats.total_questions += len(questions)
    stats.total_ok += ok_count
    stats.total_improve += improve_count
    stats.total_gap += gap_count
    stats.total_blocks_created += blocks_created
    
    logger.info(f"✓ Completed {avrop_file.name}")
    
    return {
        "questions": len(questions),
        "ok": ok_count,
        "improve": improve_count,
        "gap": gap_count,
        "blocks": blocks_created
    }


async def run_full_pipeline(
    config: Dict,
    max_files: Optional[int] = None,
    resume_from: Optional[int] = None
):
    """
    Kör hela Pipeline 2.0 med per-avrop-flöde.
    """
    start_time = datetime.now()
    
    stats = PipelineStats(started_at=start_time.isoformat())
    
    logger.info("=" * 60)
    logger.info("PIPELINE 2.0 - PER-AVROP FLOW")
    logger.info("=" * 60)
    logger.info(f"Started at: {start_time}")
    
    # Paths
    secondary_dir = AI_SERVICES_DIR / config['paths']['secondary_input']
    lake_dir = AI_SERVICES_DIR / config['paths'].get('output_lake', 'storage/lake_v2')
    index_dir = AI_SERVICES_DIR / config['paths'].get('output_index', 'storage/index_v2')
    
    # Ensure directories exist
    lake_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / 'chroma').mkdir(parents=True, exist_ok=True)
    (index_dir / 'kuzu').mkdir(parents=True, exist_ok=True)
    
    # Get avrop files
    avrop_files = get_avrop_files(secondary_dir, max_files)
    
    if not avrop_files:
        logger.error(f"No avrop files found in {secondary_dir}")
        return
    
    logger.info(f"Found {len(avrop_files)} avrop files to process")
    
    # Resume support
    start_idx = resume_from if resume_from else 0
    if start_idx > 0:
        logger.info(f"Resuming from file #{start_idx}")
    
    # Process each avrop
    for i, avrop_file in enumerate(avrop_files[start_idx:], start=start_idx):
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"AVROP {i+1}/{len(avrop_files)}")
            logger.info(f"{'='*60}")
            
            await process_single_avrop(
                avrop_file=avrop_file,
                config=config,
                lake_dir=lake_dir,
                index_dir=index_dir,
                stats=stats
            )
            
            # Save progress after each avrop
            progress_path = SCRIPT_DIR / "output" / "pipeline_progress.json"
            progress = {
                "last_completed_index": i,
                "last_completed_file": avrop_file.name,
                "stats": asdict(stats)
            }
            with open(progress_path, 'w') as f:
                json.dump(progress, f, indent=2)
            
        except KeyboardInterrupt:
            logger.info(f"\nInterrupted at file #{i}. Resume with --resume-from {i}")
            stats.save(SCRIPT_DIR / "output" / "pipeline_stats_interrupted.json")
            raise
        except Exception as e:
            logger.error(f"Error processing {avrop_file.name}: {e}")
            # Continue with next file
    
    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration}")
    logger.info(f"Avrop processed: {stats.avrop_processed}")
    logger.info(f"Total questions: {stats.total_questions}")
    logger.info(f"  - OK: {stats.total_ok}")
    logger.info(f"  - IMPROVE: {stats.total_improve}")
    logger.info(f"  - GAP: {stats.total_gap}")
    logger.info(f"Blocks created: {stats.total_blocks_created}")
    logger.info(f"Dedup runs: {stats.dedup_runs}")
    logger.info("=" * 60)
    
    # Final block count
    final_blocks = len(list(lake_dir.glob("*.md")))
    logger.info(f"Final Smart Blocks in lake: {final_blocks}")
    
    # Save final report
    report = {
        "started_at": stats.started_at,
        "completed_at": end_time.isoformat(),
        "duration_seconds": duration.total_seconds(),
        **asdict(stats),
        "final_block_count": final_blocks
    }
    
    report_path = SCRIPT_DIR / "output" / f"pipeline_report_{datetime.now():%Y%m%d_%H%M%S}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved: {report_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pipeline 2.0 - Per-Avrop Smart Block Factory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exempel:
  # Kör hela pipelinen
  python -m data_pipeline_v2.run_pipeline --batch
  
  # Testa med begränsat antal avrop
  python -m data_pipeline_v2.run_pipeline --batch --max-files 5
  
  # Återuppta från avbruten körning
  python -m data_pipeline_v2.run_pipeline --batch --resume-from 10
"""
    )
    
    parser.add_argument('--batch', action='store_true', 
                       help='Kör hela pipelinen')
    parser.add_argument('--max-files', type=int,
                       help='Max antal avrop att processa')
    parser.add_argument('--resume-from', type=int,
                       help='Återuppta från filindex (0-baserat)')
    
    args = parser.parse_args()
    
    if not args.batch:
        parser.print_help()
        print("\nAnvänd --batch för att köra pipelinen")
        return
    
    config = load_config()
    
    asyncio.run(run_full_pipeline(
        config=config,
        max_files=args.max_files,
        resume_from=args.resume_from
    ))


if __name__ == "__main__":
    main()
