#!/usr/bin/env python3
"""
Procurement Simulation Tool v3.2
Stresstesta Reasoning Engine med verkliga avropsunderlag.

AI:n spelar en beställar-persona som svarar på P-Bots frågor
baserat på scenariot tills avropsunderlaget är komplett.

Efter varje konversation skriver Gemini en berättelse från personans
perspektiv om hur de upplevde samtalet med P-Bot.

Usage:
    python tools/simulate_procurement.py              # Interaktivt läge
    python tools/simulate_procurement.py --batch      # Kör alla scenarion automatiskt
    python tools/simulate_procurement.py --clean      # Rensa gamla loggar först

Placera dina .txt-filer med avropsunderlag i test_data/scenarios/
Verktyget listar tillgängliga filer och låter dig välja.

Output:
    Konversationsloggar: tools/output/simulation_*.json
    Personaberättelser: tools/output/simulation_*_story.txt
    Gamla loggar behålls (använd --clean för att rensa)
"""
import sys
import os
import json
import requests
import datetime
import argparse
import logging
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich import box
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
except ImportError:
    print("Rich saknas. Kör: pip install rich")
    sys.exit(1)

try:
    from google import genai
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("google-genai eller python-dotenv saknas.")
    sys.exit(1)

# --- CONFIG ---
API_URL = "http://localhost:5000/api/conversation"
SCENARIOS_DIR = Path(__file__).resolve().parent.parent / "test_data" / "scenarios"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
MAX_TURNS = 15  # Säkerhetsgräns för antal rundor

console = Console(width=110)


def clean_old_logs():
    """
    Rensa gamla simuleringsloggar från output-mappen vid omstart.
    Tar bort alla simulation_*.json, *_story.txt och batch_summary_*.json filer.
    """
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return 0
    
    patterns = ["simulation_*.json", "batch_summary_*.json", "*_story.txt"]
    removed_count = 0
    
    for pattern in patterns:
        for filepath in OUTPUT_DIR.glob(pattern):
            try:
                filepath.unlink()
                removed_count += 1
            except Exception as e:
                console.print(f"[yellow]Kunde inte ta bort {filepath.name}: {e}[/yellow]")
    
    return removed_count

# Setup logging for batch mode
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- PERSONA LOADER ---
def load_persona(scenario_path: Path, quiet: bool = False) -> tuple[dict, str]:
    """
    Load persona from file or generate if not found.
    
    Looks for a file named {scenario_name}_persona.txt next to the scenario.
    Returns (persona_dict, persona_raw_text)
    """
    # Look for persona file
    persona_path = scenario_path.with_name(scenario_path.stem + "_persona.txt")
    
    if persona_path.exists():
        if not quiet:
            console.print(f"[dim]Läser persona från {persona_path.name}...[/dim]")
        persona_text = persona_path.read_text(encoding='utf-8')
        persona = parse_persona_file(persona_text)
        return persona, persona_text
    else:
        if not quiet:
            console.print(f"[yellow]Ingen persona-fil hittades ({persona_path.name})[/yellow]")
            console.print("[dim]Genererar persona automatiskt...[/dim]")
        persona = generate_persona_from_scenario(scenario_path.read_text(encoding='utf-8'))
        return persona, ""


def parse_persona_file(content: str) -> dict:
    """Parse persona text file into structured dict."""
    persona = {
        "name": "Okänd",
        "title": "Okänd",
        "organization": "Okänd",
        "personality": "",
        "knowledge_level": "Medel",
        "communication_style": "Kortfattad",
        "hidden_constraints": [],
        "goals": [],
        "background": "",
        "typical_phrases": []
    }
    
    lines = content.split('\n')
    current_section = None
    section_content = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check for markdown-style headers
        if line_stripped.startswith("**Namn:**") or line_stripped.startswith("- **Namn:**"):
            persona["name"] = line_stripped.split("**Namn:**")[-1].strip().rstrip("*").strip()
        elif line_stripped.startswith("**Titel:**") or line_stripped.startswith("- **Titel:**"):
            persona["title"] = line_stripped.split("**Titel:**")[-1].strip().rstrip("*").strip()
        elif line_stripped.startswith("**Organisation:**") or line_stripped.startswith("- **Organisation:**"):
            persona["organization"] = line_stripped.split("**Organisation:**")[-1].strip().rstrip("*").strip()
        # Check for section headers
        elif "## Personlighet" in line_stripped:
            current_section = "personality"
            section_content = []
        elif "## Kunskapsnivå" in line_stripped:
            if current_section == "personality":
                persona["personality"] = " ".join(section_content).strip()
            current_section = "knowledge"
            section_content = []
        elif "## Kommunikationsstil" in line_stripped:
            if current_section == "knowledge":
                persona["knowledge_level"] = " ".join(section_content).strip()
            current_section = "communication"
            section_content = []
        elif "## Dolda Fakta" in line_stripped:
            if current_section == "communication":
                persona["communication_style"] = " ".join(section_content).strip()
            current_section = "hidden"
            section_content = []
        elif "## Mål" in line_stripped:
            if current_section == "hidden":
                persona["hidden_constraints"] = [s.strip().lstrip("- ").lstrip("0123456789. ") for s in section_content if s.strip().startswith("-") or s.strip()[0:1].isdigit()]
            current_section = "goals"
            section_content = []
        elif "## Bakgrundshistoria" in line_stripped:
            if current_section == "goals":
                persona["goals"] = [s.strip().lstrip("- ").lstrip("0123456789. ") for s in section_content if s.strip().startswith("-") or s.strip()[0:1].isdigit()]
            current_section = "background"
            section_content = []
        elif current_section and line_stripped and not line_stripped.startswith("#"):
            section_content.append(line_stripped)
    
    # Handle last section
    if current_section == "background":
        persona["background"] = " ".join(section_content).strip()
    elif current_section == "goals":
        persona["goals"] = [s.strip().lstrip("- ").lstrip("0123456789. ") for s in section_content if s.strip().startswith("-") or s.strip()[0:1].isdigit()]
    
    return persona


def generate_persona_from_scenario(scenario_content: str) -> dict:
    """Generate a fictional persona based on the scenario (fallback)."""
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    prompt = f"""
Baserat på följande avropsunderlag, skapa en fiktiv beställare-persona.

UNDERLAG:
{scenario_content}

Returnera JSON med:
{{
    "name": "Förnamn Efternamn",
    "title": "Jobbtitel",
    "organization": "Organisation/förvaltning",
    "personality": "Kort beskrivning av personlighet",
    "knowledge_level": "Nybörjare/Medel/Expert",
    "communication_style": "Kortfattad/Utförlig/Teknisk",
    "hidden_constraints": ["Saker personen vet men inte nämnt ännu"],
    "goals": ["Vad personen vill uppnå"]
}}
"""
    
    try:
        from google.genai import types
        resp = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(resp.text)
    except Exception as e:
        console.print(f"[yellow]Kunde inte generera persona: {e}[/yellow]")
        return {
            "name": "Anna Lindqvist",
            "title": "IT-projektledare",
            "organization": "Okänd förvaltning",
            "personality": "Professionell och fokuserad",
            "knowledge_level": "Medel",
            "communication_style": "Kortfattad",
            "hidden_constraints": [],
            "goals": ["Få hjälp med avropet"]
        }


def generate_user_response(persona: dict, persona_raw: str, scenario_content: str, pbot_message: str, conversation_history: list) -> str:
    """Generate a response from the persona based on P-Bot's question."""
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Build conversation context
    history_text = ""
    for msg in conversation_history[-6:]:  # Last 3 exchanges
        role = "Beställare" if msg['role'] == 'user' else "P-Bot"
        history_text += f"{role}: {msg['content'][:300]}\n\n"
    
    # Use raw persona text if available, otherwise build from dict
    if persona_raw:
        persona_section = f"""
DIN PERSONA (följ detta exakt):
{persona_raw}
"""
    else:
        persona_section = f"""
DIN PERSONA:
Namn: {persona['name']}
Titel: {persona['title']}
Organisation: {persona['organization']}
Personlighet: {persona['personality']}
Kunskapsnivå: {persona['knowledge_level']}
Kommunikationsstil: {persona['communication_style']}

DOLDA FAKTA (avslöja gradvis):
{json.dumps(persona.get('hidden_constraints', []), ensure_ascii=False)}

MÅL:
{json.dumps(persona.get('goals', []), ensure_ascii=False)}
"""
    
    system_prompt = f"""
Du spelar rollen som {persona['name']}, {persona['title']} på {persona['organization']}.

{persona_section}

AVROPSUNDERLAGET DU HAR:
{scenario_content}

REGLER FÖR DIG:
1. Svara ENDAST som {persona['name']} - du är beställaren, inte en AI.
2. Svara på P-Bots frågor baserat på underlaget och din persona.
3. Om P-Bot frågar något du inte vet, säg det ärligt.
4. Avslöja "dolda fakta" gradvis när det blir relevant i samtalet.
5. Var naturlig - säg "jag", "vi", "vår förvaltning" etc.
6. Håll svaren korta och relevanta (max 2-3 meningar).
7. Om P-Bot ber dig bekräfta något, bekräfta eller korrigera.
8. Använd gärna "typiska fraser" från din persona.

TIDIGARE KONVERSATION:
{history_text}

P-BOT SÄGER NU:
{pbot_message}

SVARA SOM {persona['name'].upper()}:
"""
    
    try:
        resp = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=system_prompt
        )
        return resp.text.strip()
    except Exception as e:
        console.print(f"[red]Fel vid generering av svar: {e}[/red]")
        return "Jag förstår. Kan du förklara mer?"


def print_header():
    """Print tool header."""
    console.print(Panel(
        "[bold white]Procurement Simulation Tool v3.0[/bold white]\n"
        "[dim]AI-driven konversationssimulering med beställar-persona[/dim]",
        style="on blue",
        box=box.DOUBLE,
        expand=False
    ))


def list_scenarios() -> list:
    """List all scenario .txt files in scenarios directory (exclude persona files)."""
    if not SCENARIOS_DIR.exists():
        console.print(f"[red]Mappen {SCENARIOS_DIR} finns inte![/red]")
        return []
    
    # Get all .txt files that are not persona files
    scenarios = [
        f for f in SCENARIOS_DIR.glob("*.txt")
        if not f.name.endswith("_persona.txt")
    ]
    return sorted(scenarios, key=lambda x: x.name)


def select_scenario(scenarios: list) -> Path:
    """Interactive menu to select a scenario."""
    if not scenarios:
        console.print("[yellow]Inga scenarion hittades i test_data/scenarios/[/yellow]")
        console.print("[dim]Lägg till .txt-filer med avropsunderlag och kör igen.[/dim]")
        sys.exit(0)
    
    console.print("\n[bold cyan]Tillgängliga scenarion:[/bold cyan]")
    
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=4)
    table.add_column("Filnamn", style="cyan")
    table.add_column("Storlek", style="dim", justify="right")
    table.add_column("Persona", style="dim")
    
    for i, scenario in enumerate(scenarios, 1):
        size_kb = scenario.stat().st_size / 1024
        persona_path = scenario.with_name(scenario.stem + "_persona.txt")
        has_persona = "✓" if persona_path.exists() else "—"
        table.add_row(str(i), scenario.name, f"{size_kb:.1f} KB", has_persona)
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[bold green]Välj scenario[/bold green]",
        choices=[str(i) for i in range(1, len(scenarios) + 1)],
        default="1"
    )
    
    return scenarios[int(choice) - 1]


def send_to_api(message: str, history: list, session_state: dict = None) -> dict:
    """Send message to API and return response."""
    payload = {
        "user_message": message,
        "conversation_history": history,
        "session_state": session_state
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ Kunde inte ansluta till API:et![/red]")
        console.print("[dim]Starta servern med: python -m app.main[/dim]")
        raise
    except requests.exceptions.Timeout:
        console.print("[red]❌ Timeout - API:et svarade inte inom 120 sekunder[/red]")
        raise
    except Exception as e:
        console.print(f"[red]❌ API-fel: {e}[/red]")
        raise


def print_persona(persona: dict):
    """Print persona information."""
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=22)
    grid.add_column()
    
    grid.add_row("Namn:", persona.get('name', '?'))
    grid.add_row("Titel:", persona.get('title', '?'))
    grid.add_row("Organisation:", persona.get('organization', '?'))
    grid.add_row("Personlighet:", persona.get('personality', '?')[:60] + "..." if len(persona.get('personality', '')) > 60 else persona.get('personality', '?'))
    grid.add_row("Upphandlingskunskap:", persona.get('knowledge_level', '?'))
    grid.add_row("Kommunikationsstil:", persona.get('communication_style', '?'))
    
    # Show goals
    goals = persona.get('goals', [])
    if goals:
        grid.add_row("Mål:", goals[0] if goals else '?')
    
    # Show hidden constraints count
    hidden = persona.get('hidden_constraints', [])
    if hidden:
        grid.add_row("Dolda fakta:", f"[dim]{len(hidden)} st (avslöjas gradvis)[/dim]")
    
    console.print(Panel(
        grid,
        title="[bold yellow]👤 BESTÄLLAR-PERSONA[/bold yellow]",
        border_style="yellow",
        expand=False
    ))


def print_turn_header(turn: int, role: str, persona_name: str = None):
    """Print turn header."""
    if role == "user":
        name = persona_name or "BESTÄLLARE"
        console.print(f"\n[bold green]═══ RUNDA {turn} - {name.upper()} ═══[/bold green]")
    else:
        console.print(f"\n[bold red]═══ RUNDA {turn} - P-BOT ═══[/bold red]")


def print_user_message(message: str, persona_name: str):
    """Print user message."""
    console.print(Panel(
        message,
        title=f"[bold green]💬 {persona_name}[/bold green]",
        border_style="green",
        expand=False
    ))


def print_ai_response(response: dict):
    """Print AI response with analysis."""
    message = response.get('message', '')
    reasoning = response.get('reasoning', {})
    ui_directives = response.get('ui_directives', {})
    current_state = response.get('current_state', {})
    
    # Intent & Tone summary
    intent = ui_directives.get('current_intent', '?')
    tone = reasoning.get('tone', '?')
    topics = ui_directives.get('detected_topics', [])
    branches = ui_directives.get('taxonomy_branches', [])
    
    intent_color = 'green' if intent == 'FACT' else 'yellow' if intent == 'INSPIRATION' else 'blue'
    tone_color = 'red' if tone == 'Strict/Warning' else 'yellow' if tone == 'Helpful/Guiding' else 'green'
    
    # Analysis bar
    analysis = f"[{intent_color}]{intent}[/] | [{tone_color}]{tone}[/]"
    if topics:
        analysis += f" | Topics: {', '.join(topics[:3])}"
    if branches:
        analysis += f" | Branches: {', '.join(branches[:3])}"
    
    console.print(f"[dim]📊 {analysis}[/dim]")
    
    # AI Message
    console.print(Panel(
        Markdown(message),
        title="[bold red]🤖 P-Bot[/bold red]",
        border_style="red",
        expand=False
    ))
    
    # Entity summary (Varukorgen)
    entity_summary = ui_directives.get('entity_summary', {})
    resources = entity_summary.get('resources', [])
    
    if resources:
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold green", title="📦 Varukorg")
        table.add_column("Roll", style="cyan")
        table.add_column("Nivå", justify="center")
        table.add_column("Antal", justify="center")
        table.add_column("Status")
        
        for res in resources:
            level = res.get('level', '?')
            level_str = f"[red]{level}[/red]" if level and str(level) >= '4' else str(level)
            table.add_row(
                res.get('role', '?'),
                level_str,
                str(res.get('quantity', 1)),
                res.get('status', '?')
            )
        
        console.print(table)
    
    # Missing info
    missing = current_state.get('missing_info', [])
    if missing:
        console.print(f"[yellow]⚠️ Saknas: {', '.join(missing[:5])}[/yellow]")


def is_conversation_complete(response: dict, turn: int) -> bool:
    """Check if the conversation seems complete."""
    current_state = response.get('current_state', {})
    ui_directives = response.get('ui_directives', {})
    reasoning = response.get('reasoning', {})
    
    # Check for completion indicators
    missing = current_state.get('missing_info', [])
    target_step = ui_directives.get('target_step', '')
    entity_summary = ui_directives.get('entity_summary', {})
    resources = entity_summary.get('resources', [])
    
    # If we're at strategy step and have resources, likely complete
    if target_step == 'step_4_strategy' and resources:
        return True
    
    # If no missing info and we have resources
    if not missing and resources and turn >= 3:
        return True
    
    # If we have multiple resources and are past turn 5
    if len(resources) >= 2 and turn >= 5:
        return True
    
    return False


def save_conversation_log(scenario_path: Path, persona: dict, conversation: list, final_state: dict) -> Path:
    """Save complete conversation to log file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    scenario_name = scenario_path.stem.replace("scenario_", "")
    log_filename = f"simulation_{scenario_name}_{timestamp}.json"
    log_path = OUTPUT_DIR / log_filename
    
    # Build log entry
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scenario": {
            "filename": scenario_path.name,
            "path": str(scenario_path)
        },
        "persona": persona,
        "conversation": conversation,
        "final_state": final_state,
        "summary": {
            "total_turns": len([c for c in conversation if c['role'] == 'user']),
            "final_resources": len(final_state.get('ui_directives', {}).get('entity_summary', {}).get('resources', [])),
            "final_step": final_state.get('ui_directives', {}).get('target_step', 'unknown'),
            "final_intent": final_state.get('ui_directives', {}).get('current_intent', 'unknown')
        }
    }
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, ensure_ascii=False, indent=2)
    
    console.print(f"\n[dim]📝 Konversation sparad: {log_path}[/dim]")
    
    return log_path


def evaluate_user_experience(conversation: list, persona: dict, log_path: Path) -> dict:
    """
    Låt Gemini skriva en berättelse från personans perspektiv om upplevelsen.
    Sparar berättelsen i en separat textfil.
    """
    # Extrahera endast meddelanden (inte bot-resonemang)
    messages_only = []
    for msg in conversation:
        role = "Jag" if msg['role'] == 'user' else "P-Bot"
        content = msg.get('content', '')
        messages_only.append(f"{role}: {content}")
    
    conversation_text = "\n\n".join(messages_only)
    
    # Persona-kontext
    persona_name = persona.get('name', 'Okänd')
    persona_context = f"""
Namn: {persona_name}
Roll: {persona.get('title', 'Okänd')}
Organisation: {persona.get('organization', 'Okänd')}
Personlighet: {persona.get('personality', 'Okänd')}
Mål med samtalet: {', '.join(persona.get('goals', ['Okänt']))}
Dolda bekymmer: {', '.join(persona.get('hidden_constraints', ['Inga']))}
"""
    
    evaluation_prompt = f"""Du är {persona_name}. Du har precis avslutat ett samtal med en AI-assistent som heter P-Bot på Adda. P-Bot ska hjälpa dig att göra avrop på IT-konsulter via ramavtal.

DIN BAKGRUND:
{persona_context}

SAMTALET SOM ÄGDE RUM:
{conversation_text}

---

Skriv nu en berättelse (3-5 stycken) där du berättar om din upplevelse av samtalet. Skriv i första person, som om du berättar för en kollega över en fika dagen efter.

Berätta:
- Hur du kände dig när du startade samtalet och vad du hoppades på
- Vad som hände under samtalet - de avgörande ögonblicken, vändpunkterna
- Specifika saker som botten sa eller gjorde som påverkade dig
- Hur du kände dig när det var över
- Om du skulle använda tjänsten igen och varför/varför inte

Var ärlig och mänsklig. Använd din personlighet från beskrivningen ovan.
Om du är stressad och otålig - låt det synas i hur du berättar.
Om du är metodisk och noggrann - berätta så.
Om du blev frustrerad, arg, eller uppgiven - berätta det rakt ut.
Om något faktiskt fungerade bra - lyft fram det.

Skriv på svenska. Inga listor, ingen gradering, inga punkter - bara din historia som en sammanhängande berättelse.
"""

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=evaluation_prompt
        )
        
        story = response.text.strip()
        
    except Exception as e:
        story = f"[Kunde inte generera berättelse: {e}]"
    
    # Spara till separat textfil
    story_log_path = log_path.with_name(log_path.stem + "_story.txt")
    
    # Skapa en snygg header
    story_header = f"""╔══════════════════════════════════════════════════════════════════════════════╗
║  {persona_name}s berättelse
║  {persona.get('title', '')} på {persona.get('organization', '')}
║  
║  Samtal: {len(conversation)} meddelanden
║  Datum: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
╚══════════════════════════════════════════════════════════════════════════════╝

"""
    
    with open(story_log_path, 'w', encoding='utf-8') as f:
        f.write(story_header + story)
    
    console.print(f"[dim]📖 Berättelse sparad: {story_log_path}[/dim]")
    
    return {"story": story, "path": str(story_log_path), "persona_name": persona_name}


def print_evaluation_summary(evaluation: dict):
    """Print the persona's story about their experience."""
    story = evaluation.get('story', '')
    persona_name = evaluation.get('persona_name', 'Personan')
    
    if not story or story.startswith('[Kunde inte'):
        console.print(f"[red]❌ {story}[/red]")
        return
    
    console.print("\n" + "─" * 80)
    console.print(f"[bold magenta]📖 {persona_name.upper()}S BERÄTTELSE[/bold magenta]")
    console.print("─" * 80)
    
    # Print story with nice formatting
    console.print(Panel(
        Markdown(story),
        border_style="magenta",
        expand=False,
        padding=(1, 2)
    ))


def print_final_summary(conversation: list, final_response: dict, persona: dict):
    """Print final summary of the conversation."""
    console.print("\n" + "═" * 80)
    console.print("[bold white]📋 SLUTRAPPORT[/bold white]")
    console.print("═" * 80)
    
    # Persona
    console.print(f"\n[bold]Beställare:[/bold] {persona.get('name', '?')} ({persona.get('title', '?')})")
    
    # Conversation stats
    user_turns = len([c for c in conversation if c['role'] == 'user'])
    ai_turns = len([c for c in conversation if c['role'] == 'assistant'])
    
    console.print(f"\n[bold]Konversationsstatistik:[/bold]")
    console.print(f"  • Beställarmeddelanden: {user_turns}")
    console.print(f"  • P-Bot-svar: {ai_turns}")
    
    # Final state
    ui_directives = final_response.get('ui_directives', {})
    entity_summary = ui_directives.get('entity_summary', {})
    resources = entity_summary.get('resources', [])
    
    console.print(f"\n[bold]Slutresultat (Varukorg):[/bold]")
    if resources:
        for i, res in enumerate(resources, 1):
            role = res.get('role', '?')
            level = res.get('level', '?')
            quantity = res.get('quantity', 1)
            status = res.get('status', '?')
            console.print(f"  {i}. {role} - Nivå {level} x{quantity} [{status}]")
    else:
        console.print("  [yellow]Inga resurser extraherades[/yellow]")
    
    # Global fields
    location = entity_summary.get('location')
    volume = entity_summary.get('volume')
    start_date = entity_summary.get('start_date')
    
    if any([location, volume, start_date]):
        console.print(f"\n[bold]Globala fält:[/bold]")
        if location:
            console.print(f"  • Plats: {location}")
        if volume:
            console.print(f"  • Volym: {volume}")
        if start_date:
            console.print(f"  • Startdatum: {start_date}")
    
    # Final step
    target_step = ui_directives.get('target_step', 'unknown')
    console.print(f"\n[bold]Avslutat på steg:[/bold] {target_step}")
    
    # Check for N4+ roles
    n4_roles = [r for r in resources if r.get('level') and str(r.get('level', '0')) >= '4']
    if n4_roles:
        console.print(f"\n[red]⚠️ {len(n4_roles)} roller på Nivå 4+ - kräver FKU![/red]")


def run_single_scenario(scenario_path: Path, auto_mode: bool = True, quiet: bool = False) -> dict:
    """Run a single scenario and return results."""
    if not quiet:
        console.print(f"\n[dim]Läser {scenario_path.name}...[/dim]")
    
    scenario_content = scenario_path.read_text(encoding='utf-8')
    
    if not quiet:
        console.print(Panel(
            f"[bold]Fil:[/bold] {scenario_path.name}\n"
            f"[bold]Längd:[/bold] {len(scenario_content)} tecken ({len(scenario_content.split())} ord)",
            title="[bold blue]📄 SCENARIO[/bold blue]",
            border_style="blue",
            expand=False
        ))
    
    # Load or generate persona
    persona, persona_raw = load_persona(scenario_path, quiet=quiet)
    
    if not quiet:
        print_persona(persona)
    
    # Initialize conversation
    conversation = []
    history = []
    session_state = None
    turn = 0
    final_response = None
    
    if not quiet:
        console.print("\n[bold cyan]═══ KONVERSATION STARTAR ═══[/bold cyan]")
    
    # First message from "beställare"
    goals = persona.get('goals', ['genomföra en upphandling'])
    first_goal = goals[0].lower() if goals else 'genomföra en upphandling'
    first_message = f"Hej! Jag heter {persona['name']} och jobbar som {persona['title']} på {persona['organization']}. Jag behöver hjälp med ett avrop. Vi ska {first_goal}."
    
    try:
        while turn < MAX_TURNS:
            turn += 1
            
            # Get user input
            if not quiet:
                print_turn_header(turn, "user", persona['name'])
            
            if turn == 1:
                user_message = first_message
            else:
                # Generate response from persona
                if not quiet:
                    with console.status(f"[bold green]{persona['name']} tänker...[/bold green]", spinner="dots"):
                        user_message = generate_user_response(
                            persona,
                            persona_raw,
                            scenario_content, 
                            conversation[-1]['content'] if conversation else "",
                            conversation
                        )
                else:
                    user_message = generate_user_response(
                        persona,
                        persona_raw,
                        scenario_content, 
                        conversation[-1]['content'] if conversation else "",
                        conversation
                    )
            
            if not quiet:
                print_user_message(user_message, persona['name'])
            
            # Store in conversation log
            conversation.append({
                "role": "user",
                "content": user_message,
                "turn": turn
            })
            
            # Send to API
            if not quiet:
                print_turn_header(turn, "assistant")
                with console.status("[bold red]P-Bot resonerar...[/bold red]", spinner="dots"):
                    response = send_to_api(user_message, history, session_state)
            else:
                response = send_to_api(user_message, history, session_state)
            
            # Print response
            if not quiet:
                print_ai_response(response)
            
            # Store in conversation log
            conversation.append({
                "role": "assistant",
                "content": response.get('message', ''),
                "turn": turn,
                "reasoning": response.get('reasoning', {}),
                "ui_directives": response.get('ui_directives', {})
            })
            
            # Update history and state
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": response.get('message', '')})
            session_state = response.get('current_state')
            final_response = response
            
            # Check if complete
            if is_conversation_complete(response, turn):
                if not quiet:
                    console.print("\n[green]✓ Konversationen verkar komplett![/green]")
                break
            
            # Pause between turns
            if turn < MAX_TURNS:
                import time
                time.sleep(0.5)  # Small pause for API
        
        if turn >= MAX_TURNS and not quiet:
            console.print(f"\n[yellow]⚠️ Max antal rundor ({MAX_TURNS}) nått. Avslutar.[/yellow]")
    
    except KeyboardInterrupt:
        if not quiet:
            console.print("\n[yellow]Konversation avbruten av användaren.[/yellow]")
    except Exception as e:
        logger.error(f"Fel i scenario {scenario_path.name}: {e}")
        if not quiet:
            console.print(f"\n[red]❌ Fel: {e}[/red]")
    
    finally:
        # ALWAYS save log
        result = {
            "scenario": scenario_path.name,
            "persona": persona.get('name', '?'),
            "turns": turn,
            "success": final_response is not None,
            "log_path": None,
            "resources": 0,
            "evaluation": None
        }
        
        if conversation:
            state_to_save = final_response if final_response else {
                "ui_directives": {},
                "current_state": {},
                "message": "Konversation avbruten"
            }
            
            if not quiet and final_response:
                print_final_summary(conversation, final_response, persona)
            
            log_path = save_conversation_log(scenario_path, persona, conversation, state_to_save)
            
            result["log_path"] = str(log_path)
            result["resources"] = len(state_to_save.get('ui_directives', {}).get('entity_summary', {}).get('resources', []))
            
            # Generate persona's story about the experience
            if len(conversation) >= 2:  # Minst en fråga och ett svar
                if not quiet:
                    console.print("\n[dim]Låter personan berätta sin historia...[/dim]")
                    with console.status("[bold magenta]Gemini skriver berättelsen...[/bold magenta]", spinner="dots"):
                        evaluation = evaluate_user_experience(conversation, persona, log_path)
                    print_evaluation_summary(evaluation)
                else:
                    # Quiet mode - just save story
                    evaluation = evaluate_user_experience(conversation, persona, log_path)
                
                result["evaluation"] = {
                    "story": evaluation.get('story', '')[:200] + "...",  # Preview
                    "story_path": evaluation.get('path')
                }
    
    return result


def run_batch_mode():
    """Run all scenarios in batch mode."""
    print_header()
    console.print("\n[bold yellow]🔄 BATCH-LÄGE - Kör alla scenarion automatiskt[/bold yellow]\n")
    
    scenarios = list_scenarios()
    if not scenarios:
        console.print("[red]Inga scenarion hittades![/red]")
        return
    
    console.print(f"[bold]Hittade {len(scenarios)} scenarion att köra:[/bold]")
    for s in scenarios:
        persona_path = s.with_name(s.stem + "_persona.txt")
        has_persona = "✓" if persona_path.exists() else "✗"
        console.print(f"  • {s.name} [{has_persona} persona]")
    
    console.print()
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Kör scenarion...", total=len(scenarios))
        
        for scenario in scenarios:
            progress.update(task, description=f"[cyan]Kör: {scenario.stem}")
            
            try:
                result = run_single_scenario(scenario, auto_mode=True, quiet=True)
                results.append(result)
                
                # Quick status update
                status = "[green]✓[/green]" if result['success'] else "[red]✗[/red]"
                console.print(f"  {status} {scenario.name}: {result['turns']} rundor, {result['resources']} resurser")
                
            except Exception as e:
                console.print(f"  [red]✗[/red] {scenario.name}: Fel - {e}")
                results.append({
                    "scenario": scenario.name,
                    "persona": "?",
                    "turns": 0,
                    "success": False,
                    "log_path": None,
                    "resources": 0,
                    "error": str(e)
                })
            
            progress.advance(task)
    
    # Print batch summary
    console.print("\n" + "═" * 80)
    console.print("[bold white]📊 BATCH-SAMMANFATTNING[/bold white]")
    console.print("═" * 80)
    
    successful = sum(1 for r in results if r['success'])
    total_turns = sum(r['turns'] for r in results)
    total_resources = sum(r['resources'] for r in results)
    
    console.print(f"\n[bold]Resultat:[/bold]")
    console.print(f"  • Lyckade: {successful}/{len(results)}")
    console.print(f"  • Totalt antal rundor: {total_turns}")
    console.print(f"  • Totalt antal resurser extraherade: {total_resources}")
    
    # Summary table
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Scenario", style="cyan")
    table.add_column("Persona", style="yellow")
    table.add_column("Rundor", justify="center")
    table.add_column("Resurser", justify="center")
    table.add_column("Berättelse", justify="center")
    table.add_column("Status")
    
    for r in results:
        status = "[green]✓[/green]" if r['success'] else "[red]✗[/red]"
        
        # Check if story was generated
        eval_data = r.get('evaluation', {}) or {}
        has_story = "[green]📖[/green]" if eval_data.get('story') else "[dim]-[/dim]"
        
        table.add_row(
            r['scenario'],
            r['persona'],
            str(r['turns']),
            str(r['resources']),
            has_story,
            status
        )
    
    console.print(table)
    
    # Count stories
    story_count = sum(1 for r in results if r.get('evaluation', {}).get('story'))
    if story_count > 0:
        console.print(f"\n[bold magenta]📖 {story_count} berättelser genererade[/bold magenta]")
        console.print("[dim]Läs dem i output/-mappen (*_story.txt)[/dim]")
    
    # Save batch summary
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    summary_path = OUTPUT_DIR / f"batch_summary_{timestamp}.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.datetime.now().isoformat(),
            "total_scenarios": len(results),
            "successful": successful,
            "total_turns": total_turns,
            "total_resources": total_resources,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    console.print(f"\n[dim]📝 Batch-sammanfattning sparad: {summary_path}[/dim]")


def run_interactive_mode():
    """Run interactive mode (original behavior)."""
    print_header()
    
    # List and select scenario
    scenarios = list_scenarios()
    scenario_path = select_scenario(scenarios)
    
    # Read scenario content
    console.print(f"\n[dim]Läser {scenario_path.name}...[/dim]")
    scenario_content = scenario_path.read_text(encoding='utf-8')
    
    console.print(Panel(
        f"[bold]Fil:[/bold] {scenario_path.name}\n"
        f"[bold]Längd:[/bold] {len(scenario_content)} tecken ({len(scenario_content.split())} ord)",
        title="[bold blue]📄 SCENARIO[/bold blue]",
        border_style="blue",
        expand=False
    ))
    
    # Load or generate persona
    with console.status("[bold yellow]Laddar persona...[/bold yellow]", spinner="dots"):
        persona, persona_raw = load_persona(scenario_path)
    
    print_persona(persona)
    
    # Ask for mode
    auto_mode = Confirm.ask(
        "\n[bold]Automatiskt läge?[/bold] (AI spelar beställaren)",
        default=True
    )
    
    # Initialize conversation - these need to be accessible for cleanup
    conversation = []
    history = []
    session_state = None
    turn = 0
    final_response = None
    
    console.print("\n[bold cyan]═══ KONVERSATION STARTAR ═══[/bold cyan]")
    
    # First message from "beställare"
    goals = persona.get('goals', ['genomföra en upphandling'])
    first_goal = goals[0].lower() if goals else 'genomföra en upphandling'
    first_message = f"Hej! Jag heter {persona['name']} och jobbar som {persona['title']} på {persona['organization']}. Jag behöver hjälp med ett avrop. Vi ska {first_goal}."
    
    try:
        while turn < MAX_TURNS:
            turn += 1
            
            # Get user input
            print_turn_header(turn, "user", persona['name'])
            
            if turn == 1:
                user_message = first_message
            elif auto_mode:
                # Generate response from persona
                with console.status(f"[bold green]{persona['name']} tänker...[/bold green]", spinner="dots"):
                    user_message = generate_user_response(
                        persona,
                        persona_raw,
                        scenario_content, 
                        conversation[-1]['content'] if conversation else "",
                        conversation
                    )
            else:
                # Manual mode
                user_message = Prompt.ask(f"[bold green]{persona['name']}[/bold green]")
                if user_message.lower() in ['exit', 'quit', 'sluta', 'avsluta']:
                    console.print("[dim]Konversation avbruten.[/dim]")
                    break
            
            print_user_message(user_message, persona['name'])
            
            # Store in conversation log
            conversation.append({
                "role": "user",
                "content": user_message,
                "turn": turn
            })
            
            # Send to API
            print_turn_header(turn, "assistant")
            with console.status("[bold red]P-Bot resonerar...[/bold red]", spinner="dots"):
                response = send_to_api(user_message, history, session_state)
            
            # Print response
            print_ai_response(response)
            
            # Store in conversation log
            conversation.append({
                "role": "assistant",
                "content": response.get('message', ''),
                "turn": turn,
                "reasoning": response.get('reasoning', {}),
                "ui_directives": response.get('ui_directives', {})
            })
            
            # Update history and state
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": response.get('message', '')})
            session_state = response.get('current_state')
            final_response = response
            
            # Check if complete
            if is_conversation_complete(response, turn):
                console.print("\n[green]✓ Konversationen verkar komplett![/green]")
                break
            
            # Pause between turns in auto mode
            if auto_mode and turn < MAX_TURNS:
                import time
                time.sleep(1)  # Small pause for readability
        
        if turn >= MAX_TURNS:
            console.print(f"\n[yellow]⚠️ Max antal rundor ({MAX_TURNS}) nått. Avslutar.[/yellow]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Konversation avbruten av användaren.[/yellow]")
    
    finally:
        # ALWAYS save log, even if conversation was interrupted
        if conversation:
            console.print("\n[dim]Sparar sessionslogg...[/dim]")
            
            # Use final_response if available, otherwise create minimal state
            state_to_save = final_response if final_response else {
                "ui_directives": {},
                "current_state": {},
                "message": "Konversation avbruten"
            }
            
            # Print summary if we have a complete response
            if final_response:
                print_final_summary(conversation, final_response, persona)
            
            # Always save the log
            log_path = save_conversation_log(scenario_path, persona, conversation, state_to_save)
            
            # Generate persona's story about the experience
            if len(conversation) >= 2:  # Minst en fråga och ett svar
                console.print("\n[dim]Låter personan berätta sin historia...[/dim]")
                with console.status("[bold magenta]Gemini skriver berättelsen...[/bold magenta]", spinner="dots"):
                    evaluation = evaluate_user_experience(conversation, persona, log_path)
                print_evaluation_summary(evaluation)
        else:
            console.print("[yellow]Ingen konversation att spara.[/yellow]")


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description="Procurement Simulation Tool")
    parser.add_argument("--batch", action="store_true", help="Kör alla scenarion automatiskt")
    parser.add_argument("--clean", action="store_true", help="Rensa gamla loggar innan körning")
    args = parser.parse_args()
    
    # Rensa gamla loggar endast om --clean anges
    if args.clean:
        removed = clean_old_logs()
        if removed > 0:
            console.print(f"[dim]🧹 Rensade {removed} gamla loggfil(er) från output/[/dim]\n")
    
    try:
        if args.batch:
            run_batch_mode()
        else:
            run_interactive_mode()
    except Exception as e:
        console.print(f"\n[red]❌ Fel: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
