"""
Pipeline 2.0 - Tester

Testar frågor mot P-Bot och använder Judge-LLM för att bedöma svaret.

Input: Lista med ExtractedQuestion
Output: Lista med TestResult (question, bot_response, sources, verdict, judge_reasoning)
"""

import os
import json
import asyncio
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from google import genai
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "config" / "pipeline_v2_config.yaml"


class Verdict(str, Enum):
    """Resultat av Judge-bedömning."""
    OK = "OK"           # Svaret är korrekt
    IMPROVE = "IMPROVE" # Block finns men kan förbättras
    GAP = "GAP"         # Block saknas


@dataclass
class TestResult:
    """Resultat av test av en fråga."""
    question: str
    phase: str
    bot_response: str
    sources: List[str]
    verdict: Verdict
    judge_reasoning: str
    anonymized_example: Optional[str] = None
    source_avrop_id: Optional[str] = None
    decision_type: Optional[str] = None


def load_config() -> Dict:
    """Ladda pipeline config."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def ask_pbot(question: str, endpoint: str) -> Dict[str, Any]:
    """
    Skicka fråga till P-Bot API.
    
    Returns: {message, sources, thoughts, ...}
    """
    try:
        response = requests.post(
            endpoint,
            json={
                "user_message": question,
                "conversation_history": []
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"P-Bot request failed: {e}")
        return {
            "message": f"ERROR: {e}",
            "sources": []
        }


def read_source_blocks(source_files: List[str], lake_dir: Path) -> str:
    """Läs innehållet från source-block för Judge."""
    contents = []
    
    for source in source_files[:5]:  # Max 5 sources
        # Hitta filen i lake
        matches = list(lake_dir.glob(f"*{source}*"))
        if matches:
            try:
                with open(matches[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Ta bara content efter YAML frontmatter
                    if '---' in content:
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            content = parts[2].strip()
                    contents.append(f"### {source}\n{content[:2000]}")
            except Exception as e:
                logger.warning(f"Could not read source {source}: {e}")
    
    return "\n\n".join(contents) if contents else "(Inga källor hittades)"


async def judge_response(
    client: genai.Client,
    question: str,
    bot_response: str,
    source_content: str,
    model_name: str
) -> tuple[Verdict, str]:
    """
    Använd Judge-LLM för att bedöma om bottens svar är korrekt.
    
    Returns: (verdict, reasoning)
    """
    
    prompt = """Du är en STRIKT faktagranskare för Addas ramavtal IT-konsulttjänster 2021.

FRÅGA SOM STÄLLDES:
{question}

BOTTENS SVAR:
{bot_response}

KÄLLOR SOM BOTTEN ANVÄNDE:
{source_content}

UPPGIFT:
Bedöm om bottens svar DIREKT SVARAR på den SPECIFIKA frågan som ställdes.

BEDÖMNINGSKRITERIER (strikt tolkning):
- CORRECT: Svaret svarar DIREKT och SPECIFIKT på frågan. Informationen stämmer med källorna.
- WRONG: Svaret motsäger eller feltolkar källorna.
- INCOMPLETE: Svaret är GENERELLT eller AVVIKANDE - pratar om annat än vad frågan handlar om.
  OBS: Ett "hjälpsamt" svar som inte adresserar EXAKT vad användaren frågade = INCOMPLETE!
- NO_SOURCES: Botten hittade inga relevanta källor eller sa "vet inte".

VIKTIGT:
- Om frågan är "Hur gör jag X?" och svaret är "Vilken roll söker du?" = INCOMPLETE
- Om frågan är specifik men svaret är generell intake-info = INCOMPLETE
- Endast om svaret DIREKT matchar frågan = CORRECT

OUTPUT FORMAT (JSON):
{{
  "verdict": "CORRECT" | "WRONG" | "INCOMPLETE" | "NO_SOURCES",
  "reasoning": "Kort motivering på svenska - förklara varför svaret matchar/inte matchar frågan"
}}
""".format(
        question=question,
        bot_response=bot_response[:3000],
        source_content=source_content[:5000]
    )

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
        verdict_str = result.get('verdict', 'NO_SOURCES')
        reasoning = result.get('reasoning', '')
        
        # Map to our Verdict enum
        if verdict_str == "CORRECT":
            return Verdict.OK, reasoning
        elif verdict_str in ["WRONG", "INCOMPLETE"]:
            return Verdict.IMPROVE, reasoning
        else:  # NO_SOURCES
            return Verdict.GAP, reasoning
            
    except Exception as e:
        logger.error(f"Judge error: {e}")
        return Verdict.GAP, f"Judge error: {e}"


async def test_question(
    question_data: Dict,
    client: genai.Client,
    config: Dict,
    lake_dir: Path
) -> TestResult:
    """
    Testa en fråga mot P-Bot och bedöm svaret.
    """
    question = question_data['question']
    phase = question_data.get('phase', 'step_1_intake')
    
    # 1. Fråga P-Bot
    endpoint = config['api']['pbot_endpoint']
    pbot_response = ask_pbot(question, endpoint)
    
    bot_message = pbot_response.get('message', '')
    sources = pbot_response.get('sources', [])
    
    # 2. Läs source-innehåll för Judge
    source_content = read_source_blocks(sources, lake_dir)
    
    # 3. Judge bedömer
    model_name = config.get('models', {}).get('judge', 'gemini-2.0-flash')
    verdict, reasoning = await judge_response(
        client=client,
        question=question,
        bot_response=bot_message,
        source_content=source_content,
        model_name=model_name
    )
    
    return TestResult(
        question=question,
        phase=phase,
        bot_response=bot_message,
        sources=sources,
        verdict=verdict,
        judge_reasoning=reasoning,
        anonymized_example=question_data.get('anonymized_example'),
        source_avrop_id=question_data.get('source_avrop_id'),
        decision_type=question_data.get('decision_type')
    )


async def test_all_questions(
    questions: List[Dict],
    config: Dict,
    lake_dir: Path,
    max_questions: Optional[int] = None
) -> List[TestResult]:
    """
    Testa alla frågor mot P-Bot.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")
    
    client = genai.Client(api_key=api_key)
    
    if max_questions:
        questions = questions[:max_questions]
    
    logger.info(f"Testing {len(questions)} questions against P-Bot...")
    
    results = []
    stats = {Verdict.OK: 0, Verdict.IMPROVE: 0, Verdict.GAP: 0}
    
    for i, q_data in enumerate(questions):
        logger.info(f"Testing {i+1}/{len(questions)}: {q_data['question'][:50]}...")
        
        result = await test_question(q_data, client, config, lake_dir)
        results.append(result)
        stats[result.verdict] += 1
        
        logger.info(f"  → Verdict: {result.verdict.value}")
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info(f"  OK:      {stats[Verdict.OK]} ({stats[Verdict.OK]/len(questions)*100:.1f}%)")
    logger.info(f"  IMPROVE: {stats[Verdict.IMPROVE]} ({stats[Verdict.IMPROVE]/len(questions)*100:.1f}%)")
    logger.info(f"  GAP:     {stats[Verdict.GAP]} ({stats[Verdict.GAP]/len(questions)*100:.1f}%)")
    logger.info("=" * 60)
    
    return results


def save_test_results(results: List[TestResult], output_path: Path):
    """Spara testresultat till JSON."""
    stats = {Verdict.OK: 0, Verdict.IMPROVE: 0, Verdict.GAP: 0}
    for r in results:
        stats[r.verdict] += 1
    
    output = {
        "total_tested": len(results),
        "stats": {
            "ok": stats[Verdict.OK],
            "improve": stats[Verdict.IMPROVE],
            "gap": stats[Verdict.GAP]
        },
        "results": [
            {**asdict(r), "verdict": r.verdict.value}
            for r in results
        ]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved results to {output_path}")


def load_extracted_questions(input_path: Path) -> List[Dict]:
    """Ladda extraherade frågor från Extractor output."""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Flatten all questions from all analyses
    questions = []
    for analysis in data.get('analyses', []):
        for q in analysis.get('questions', []):
            q['source_avrop_id'] = analysis.get('avrop_id')
            questions.append(q)
    
    return questions


async def main():
    """Main entry point for Tester."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline 2.0 - Tester")
    parser.add_argument('--input', type=str, default='extracted_questions.json',
                       help='Input fil från Extractor')
    parser.add_argument('--output', type=str, default='test_results.json',
                       help='Output fil för testresultat')
    parser.add_argument('--max-questions', type=int, help='Max antal frågor att testa')
    args = parser.parse_args()
    
    config = load_config()
    
    # Input/output paths
    input_path = SCRIPT_DIR / "output" / args.input
    output_path = SCRIPT_DIR / "output" / args.output
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Kör först: python -m data_pipeline_v2.extractor")
        return
    
    # Lake directory
    lake_dir = SCRIPT_DIR.parent / config['paths'].get('output_lake', 'storage/lake_v2')
    if not lake_dir.exists():
        # Fallback to production lake
        lake_dir = SCRIPT_DIR.parent / 'storage/lake'
    
    # Load questions
    questions = load_extracted_questions(input_path)
    logger.info(f"Loaded {len(questions)} questions from {input_path}")
    
    # Test
    results = await test_all_questions(
        questions=questions,
        config=config,
        lake_dir=lake_dir,
        max_questions=args.max_questions
    )
    
    # Save
    save_test_results(results, output_path)


if __name__ == "__main__":
    asyncio.run(main())

