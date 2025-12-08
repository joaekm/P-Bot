"""
Pipeline 2.0 - Extractor

Extraherar frågor som en beställare BORDE HA STÄLLT till P-Bot
när avropet skapades (enligt Addas process).

Input: SECONDARY-avrop (PDF/DOCX)
Output: Lista med {question, phase, anonymized_example}
"""

import os
import re
import yaml
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from google import genai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).parent
AI_SERVICES_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config" / "pipeline_v2_config.yaml"


@dataclass
class ExtractedQuestion:
    """En fråga extraherad från ett avrop."""
    question: str
    phase: str  # step_1_intake, step_2_level, step_3_volume, step_4_strategy
    anonymized_example: Optional[str] = None
    source_avrop_id: Optional[str] = None
    decision_type: Optional[str] = None  # roll, nivå, volym, avropsform, viktning, etc.
    found_in_avrop: bool = True  # True om beslutet hittades i avropet, False om det saknas


@dataclass 
class AvropAnalysis:
    """Resultat av analys av ett avrop."""
    avrop_id: str
    source_file: str
    questions: List[ExtractedQuestion] = field(default_factory=list)
    decisions_found: Dict[str, Any] = field(default_factory=dict)
    anonymization_applied: List[str] = field(default_factory=list)
    complexity: str = "normal"  # simple, normal, complex


def load_config() -> Dict:
    """Ladda pipeline config."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def anonymize_text(text: str, config: Dict) -> tuple[str, List[str]]:
    """
    Anonymisera text genom att strippa giftig data.
    
    Returns: (anonymized_text, list_of_replacements)
    """
    replacements = []
    anonymized = text
    
    toxic_patterns = config.get('anonymization', {}).get('toxic_patterns', [])
    
    for i, pattern in enumerate(toxic_patterns):
        try:
            matches = re.findall(pattern, anonymized, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                replacement = f"[ANONYMIZED_{i}]"
                anonymized = anonymized.replace(match, replacement)
                replacements.append(f"{match} -> {replacement}")
        except re.error as e:
            logger.warning(f"Invalid regex pattern: {pattern} - {e}")
    
    return anonymized, replacements


async def extract_questions_from_avrop(
    client: genai.Client,
    avrop_text: str,
    avrop_id: str,
    config: Dict,
    model_name: str
) -> AvropAnalysis:
    """
    Analysera ett avrop och extrahera frågor som beställaren borde ha ställt.
    """
    
    # Anonymisera först
    anonymized_text, replacements = anonymize_text(avrop_text, config)
    
    prompt = """Du är en expert på offentlig upphandling och Addas ramavtal IT-konsulttjänster 2021.

UPPGIFT:
Analysera detta avropsunderlag och identifiera vilka FRÅGOR en beställare 
borde ha ställt till en AI-assistent (P-Bot) när avropet skapades.

AVROPETS INNEHÅLL:
---
{avrop_text}
---

ADDAS PROCESS (4 steg) OCH ALLA BESLUTSPUNKTER:

step_1_intake (Behov):
- roll: Vilken typ av konsult? (projektledare, utvecklare, arkitekt, etc.)
- kompetensomrade: Vilket av de 7 kompetensområdena?
- region: Vilket geografiskt delområde? (A-G)
- placeringskrav: På plats, distans eller hybrid?
- antal_konsulter: Hur många konsulter behövs?
- specifika_krav: Certifieringar, säkerhetskrav, språkkrav?
- uppdragsbeskrivning: Vad ska konsulten göra?

step_2_level (Kompetensnivå):
- kompetensniva: Nivå 1-5 baserat på komplexitet och självständighet

step_3_volume (Volym & Tid):
- volym_timmar: Total uppskattad volym
- tidsram_start: När ska uppdraget börja?
- tidsram_slut: När ska uppdraget sluta?
- budget: Uppskattad budget eller takpris?

step_4_strategy (Avropsform & Utvärdering):
- avropsform: DR (rangordning) eller FKU (förnyad konkurrensutsättning)?
- viktning: Hur viktas pris vs kvalitet? (t.ex. 70/30)
- mervardeskriterier: Vilka mervärden utvärderas?
- intervjukriterier: Vad utvärderas vid intervju?
- referenser: Hur många och vilken typ?
- efterlevnad: Hur säkerställs att krav efterlevs? (vite, sanktioner)

INSTRUKTIONER:
1. Läs igenom avropet noggrant
2. För VARJE beslutspunkt som finns i avropet - skapa en fråga
3. Frågorna ska vara NATURLIGA - som en beställare faktiskt skulle fråga
4. Om en beslutspunkt SAKNAS i avropet - skapa ändå en fråga om det (markera det)
5. Inkludera anonymiserade EXEMPEL från avropet där relevant

STRATEGI FÖR ANTAL FRÅGOR:
- Om avropet är ENKELT (få beslut, kort): 4-6 frågor
- Om avropet är NORMALT: 6-10 frågor  
- Om avropet är KOMPLEXT (många krav, FKU med mervärden): 10-15 frågor
- Generera ALLTID minst en fråga per process-steg (step_1 till step_4)

OUTPUT FORMAT (JSON):
{{
  "avrop_complexity": "simple" | "normal" | "complex",
  "decisions_found": {{
    "roll": "projektledare" eller null,
    "kompetensomrade": "KO2" eller null,
    "kompetensniva": "3" eller null,
    "volym_timmar": "500" eller null,
    "tidsram_start": "2024-01-15" eller null,
    "tidsram_slut": "2024-06-30" eller null,
    "avropsform": "FKU" eller "DR" eller null,
    "viktning": "70/30" eller null,
    "region": "D" eller null,
    "placeringskrav": "på plats 3 dagar/vecka" eller null,
    "antal_konsulter": "2" eller null,
    "mervardeskriterier": ["erfarenhet", "intervju"] eller null,
    "efterlevnad": "vite vid försening" eller null
  }},
  "questions": [
    {{
      "question": "Jag behöver en projektledare, vilken nivå passar för mitt uppdrag?",
      "phase": "step_2_level",
      "decision_type": "kompetensniva",
      "anonymized_example": "Avropet använde nivå 3 för projektledare",
      "found_in_avrop": true
    }},
    {{
      "question": "Hur säkerställer jag att konsulten faktiskt är på plats de dagar vi avtalat?",
      "phase": "step_4_strategy",
      "decision_type": "efterlevnad",
      "anonymized_example": "Avropet kräver närvaro 3 dagar/vecka men nämner inga sanktioner",
      "found_in_avrop": false
    }}
  ]
}}
""".format(avrop_text=anonymized_text[:15000])  # Begränsa storlek

    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.3
            }
        )
        
        # Parse JSON response
        import json
        result = json.loads(response.text)
        
        # Build ExtractedQuestions
        questions = []
        for q in result.get('questions', []):
            questions.append(ExtractedQuestion(
                question=q.get('question', ''),
                phase=q.get('phase', 'step_1_intake'),
                anonymized_example=q.get('anonymized_example'),
                source_avrop_id=avrop_id,
                decision_type=q.get('decision_type'),
                found_in_avrop=q.get('found_in_avrop', True)
            ))
        
        return AvropAnalysis(
            avrop_id=avrop_id,
            source_file=avrop_id,
            questions=questions,
            decisions_found=result.get('decisions_found', result.get('decisions', {})),
            anonymization_applied=replacements,
            complexity=result.get('avrop_complexity', 'normal')
        )
        
    except Exception as e:
        logger.error(f"Error extracting from {avrop_id}: {e}")
        return AvropAnalysis(
            avrop_id=avrop_id,
            source_file=avrop_id,
            questions=[],
            decisions_found={},
            anonymization_applied=replacements
        )


def read_document(file_path: Path) -> Optional[str]:
    """Läs dokument (PDF, DOCX, TXT)."""
    ext = file_path.suffix.lower()
    
    try:
        if ext == '.txt' or ext == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(file_path))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            except ImportError:
                logger.error("pypdf not installed. Run: pip install pypdf")
                return None
        
        elif ext == '.docx':
            try:
                from docx import Document
                doc = Document(str(file_path))
                return "\n".join([p.text for p in doc.paragraphs])
            except ImportError:
                logger.error("python-docx not installed. Run: pip install python-docx")
                return None
        
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return None
            
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None


async def extract_all_questions(
    secondary_dir: Path,
    config: Dict,
    max_files: Optional[int] = None
) -> List[AvropAnalysis]:
    """
    Extrahera frågor från alla avrop i secondary_dir.
    """
    # Setup Gemini client
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY environment variable")
    
    client = genai.Client(api_key=api_key)
    model_name = config.get('models', {}).get('extractor', 'gemini-2.0-flash')
    
    # Find all files
    files = list(secondary_dir.glob('*'))
    files = [f for f in files if f.is_file() and f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
    
    if max_files:
        files = files[:max_files]
    
    logger.info(f"Found {len(files)} avrop files to process")
    
    results = []
    for i, file_path in enumerate(files):
        logger.info(f"Processing {i+1}/{len(files)}: {file_path.name}")
        
        text = read_document(file_path)
        if not text:
            continue
        
        analysis = await extract_questions_from_avrop(
            client=client,
            avrop_text=text,
            avrop_id=file_path.stem,
            config=config,
            model_name=model_name
        )
        
        results.append(analysis)
        logger.info(f"  → Extracted {len(analysis.questions)} questions")
    
    return results


def save_extracted_questions(
    analyses: List[AvropAnalysis],
    output_path: Path
):
    """Spara extraherade frågor till JSON."""
    import json
    
    output = {
        "total_avrop": len(analyses),
        "total_questions": sum(len(a.questions) for a in analyses),
        "analyses": [asdict(a) for a in analyses]
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {output['total_questions']} questions to {output_path}")


async def main():
    """Main entry point for Extractor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pipeline 2.0 - Extractor")
    parser.add_argument('--max-files', type=int, help='Max antal avrop att processa')
    parser.add_argument('--output', type=str, default='extracted_questions.json', 
                       help='Output fil för extraherade frågor')
    args = parser.parse_args()
    
    config = load_config()
    secondary_dir = AI_SERVICES_DIR / config['paths']['secondary_input']
    
    if not secondary_dir.exists():
        logger.error(f"Secondary directory not found: {secondary_dir}")
        logger.info("Placera SECONDARY-avrop i: data_pipeline/input/secondary/")
        return
    
    # Check if there are files
    files = list(secondary_dir.glob('*'))
    if not files:
        logger.error(f"No files found in {secondary_dir}")
        logger.info("Placera SECONDARY-avrop (PDF/DOCX) i: data_pipeline/input/secondary/")
        return
    
    analyses = await extract_all_questions(
        secondary_dir=secondary_dir,
        config=config,
        max_files=args.max_files
    )
    
    output_path = SCRIPT_DIR / "output" / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_extracted_questions(analyses, output_path)


if __name__ == "__main__":
    asyncio.run(main())

