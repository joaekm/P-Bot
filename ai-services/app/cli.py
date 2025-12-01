"""
Adda P-Bot CLI v5.4
Command-line interface for testing the search engine.

v5.4 Changes:
- Shows AvropsData (resources with DELETE support)
- Shows AvropsProgress (completion %, missing fields)
- Shows avrop_typ (DR_RESURS, FKU_RESURS, FKU_PROJEKT)

v5.2 Changes:
- Shows IntentTarget data (topics, branches, scope)
- Shows ReasoningPlan (conclusion, policy, tone)
"""
import os
import sys
import yaml
import logging
import argparse
from pathlib import Path

# Third party imports for UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import box
except ImportError:
    print("Rich saknas. Kör: pip install rich")
    sys.exit(1)

# --- ARGS (måste parsas FÖRE logging-konfiguration) ---
parser = argparse.ArgumentParser(description="Adda P-Bot CLI v5.4")
parser.add_argument("--debug", action="store_true", help="Visa tankeprocessen och engine-loggar")
args = parser.parse_args()

# --- LOGGING (baserat på debug-flagga) ---
DEBUG_MODE = args.debug

if DEBUG_MODE:
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger("ADDA_ENGINE").setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.CRITICAL)
    logging.getLogger("ADDA_ENGINE").setLevel(logging.CRITICAL)

# Tysta alltid externa bibliotek
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("google.genai").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Import Engine (EFTER logging är konfigurerat)
from .engine import AddaSearchEngine

# --- CONFIG ---
def load_config():
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "adda_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# --- SETUP ---
console = Console(width=100)
engine = AddaSearchEngine()

# --- UI HELPERS ---

def show_header():
    console.clear()
    title = f"{CONFIG['system']['app_name']} v{CONFIG['system']['version']}"
    console.print(Panel(
        f"[bold white]{title}[/bold white]\n[dim]Reasoning Engine v5.4 (AvropsData + DELETE)[/dim]", 
        style="on red", 
        box=box.DOUBLE, 
        expand=False
    ))
    if DEBUG_MODE:
        console.print("[yellow]🔧 DEBUG MODE: ON[/yellow]")


def show_intent(ui_directives):
    """Show IntentTarget data from UI directives."""
    if not ui_directives:
        return
    
    intent = ui_directives.get('current_intent', 'UNKNOWN')
    topics = ui_directives.get('detected_topics', [])
    branches = ui_directives.get('taxonomy_branches', [])
    ghost_mode = ui_directives.get('ghost_mode', False)
    
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=15)
    grid.add_column()
    
    # Intent with color
    intent_color = 'green' if intent == 'FACT' else 'yellow' if intent == 'INSPIRATION' else 'blue'
    grid.add_row("Intent:", f"[{intent_color}]{intent}[/]")
    
    # Topics
    if topics:
        grid.add_row("Topics:", ", ".join(topics[:5]))
    
    # Branches
    if branches:
        branch_str = ", ".join([f"[magenta]{b}[/magenta]" for b in branches])
        grid.add_row("Branches:", branch_str)
    
    # Ghost Mode
    if ghost_mode:
        grid.add_row("Ghost Mode:", "[red]🛡️ SECONDARY blocked[/red]")
    
    console.print(Panel(
        grid, 
        title="[bold blue]🎯 Intent Analysis[/bold blue]", 
        border_style="blue", 
        expand=False
    ))


def show_reasoning(reasoning):
    """Show ReasoningPlan from Planner."""
    if not reasoning:
        return
    
    conclusion = reasoning.get('conclusion', 'Ingen slutsats')
    policy = reasoning.get('policy', 'Ingen regel identifierad')
    tone = reasoning.get('tone', 'Informative')
    conflicts = reasoning.get('conflicts')
    validation = reasoning.get('validation')
    
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=15)
    grid.add_column()
    
    # Conclusion (truncated)
    conclusion_short = conclusion[:80] + "..." if len(conclusion) > 80 else conclusion
    grid.add_row("Slutsats:", conclusion_short)
    
    # Policy
    grid.add_row("Regel:", f"[dim]{policy}[/dim]")
    
    # Tone with color
    tone_colors = {
        'Strict/Warning': 'red',
        'Helpful/Guiding': 'yellow',
        'Informative': 'green'
    }
    tone_color = tone_colors.get(tone, 'white')
    grid.add_row("Ton:", f"[{tone_color}]{tone}[/]")
    
    # Conflicts (if any)
    if conflicts and conflicts != "null":
        grid.add_row("Konflikt:", f"[yellow]{conflicts}[/yellow]")
    
    # Validation warning (if any)
    if validation and validation != "null":
        grid.add_row("Validering:", f"[red]⚠️ {validation}[/red]")
    
    console.print(Panel(
        grid, 
        title="[bold magenta]🧠 Reasoning (Planner)[/bold magenta]", 
        border_style="magenta", 
        expand=False
    ))


def show_state(current_state, avrop_data=None, avrop_progress=None):
    """Visa AvropsData och progress (v5.4)."""
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=15)
    grid.add_column()
    
    # v5.4: Show AvropsProgress
    if avrop_progress:
        completion = avrop_progress.get('completion_percent', 0)
        is_complete = avrop_progress.get('is_complete', False)
        avrop_typ = avrop_progress.get('avrop_typ', 'UNKNOWN')
        
        # Completion bar
        completion_color = 'green' if is_complete else 'yellow' if completion > 50 else 'red'
        grid.add_row("Avrop-typ:", f"[bold]{avrop_typ}[/bold]")
        grid.add_row("Komplett:", f"[{completion_color}]{completion:.0f}%[/]" + (" ✅" if is_complete else ""))
        
        # Constraint violations
        violations = avrop_progress.get('constraint_violations', [])
        if violations:
            for v in violations[:2]:
                grid.add_row("⚠️ Regelbrott:", f"[red]{v}[/red]")
    
    # v5.4: Show AvropsData resources
    if avrop_data:
        resources = avrop_data.get('resources', [])
        if resources:
            for i, r in enumerate(resources[:5]):  # Max 5
                roll = r.get('roll', '?')
                level = r.get('level', '?')
                antal = r.get('antal', 1)
                is_complete = r.get('is_complete', False)
                status = "✅" if is_complete else "⏳"
                antal_str = f" x{antal}" if antal > 1 else ""
                grid.add_row(f"Resurs {i+1}:", f"{roll} (Nivå {level}){antal_str} {status}")
        else:
            grid.add_row("Resurser:", "[dim]Inga resurser ännu[/dim]")
        
        # Global fields
        location = avrop_data.get('location_text')
        volume = avrop_data.get('volume')
        start = avrop_data.get('start_date')
        
        global_parts = []
        if location:
            global_parts.append(f"Ort: {location}")
        if volume:
            global_parts.append(f"Volym: {volume}h")
        if start:
            global_parts.append(f"Start: {start}")
        
        if global_parts:
            grid.add_row("Globalt:", ", ".join(global_parts))
    
    # Missing fields
    if avrop_progress:
        missing = avrop_progress.get('missing_fields', [])
        if missing:
            grid.add_row("Saknas:", ", ".join(missing[:4]) + ("..." if len(missing) > 4 else ""))
    
    # Fallback to legacy current_state if no avrop_data
    if not avrop_data and current_state:
        entities = current_state.get('extracted_entities', {})
        resources = entities.get('resources', [])
        if resources:
            res_str = ", ".join([f"{r.get('role', '?')} (L{r.get('level', '?')})" for r in resources[:3]])
            grid.add_row("Resurser:", res_str)
        
        forced_strategy = current_state.get('forced_strategy')
        if forced_strategy:
            grid.add_row("Strategi:", f"[red]⚠️ {forced_strategy} (tvingad)[/red]")
    
    console.print(Panel(
        grid, 
        title="[bold green]📦 Avrop (Varukorg)[/bold green]", 
        border_style="green", 
        expand=False
    ))


def show_sources(sources):
    """Show sources used in response."""
    if not sources:
        return
    
    table = Table(
        title="Använda Källor", 
        box=box.SIMPLE, 
        width=100, 
        header_style="bold green"
    )
    table.add_column("Filnamn", style="dim")
    
    for s in sources[:10]:  # Max 10 sources
        table.add_row(s)
        
    console.print(table)


# --- MAIN LOOP ---
def chat_loop():
    show_header()
    history = []
    session_state = None
    avrop_data = None  # v5.4: Track AvropsData

    while True:
        query = Prompt.ask("\n[bold green]Du[/bold green]")
        if query.lower() in ['exit', 'quit', 'sluta']:
            break
        if not query.strip():
            continue

        with console.status("[bold red]P-Bot resonerar...[/bold red]", spinner="dots"):
            result = engine.run(query, history, session_state, avrop_data=None)
        
        # Uppdatera session state och avrop_data för nästa runda
        session_state = result.get('current_state')
        avrop_data = result.get('avrop_data')  # v5.4
        avrop_progress = result.get('avrop_progress')  # v5.4
        ui_directives = result.get('ui_directives', {})
        reasoning = result.get('reasoning', {})
        
        # 1. Visa Intent (Om debug)
        if DEBUG_MODE:
            show_intent(ui_directives)
        
        # 2. Visa Reasoning (Om debug)
        if DEBUG_MODE:
            show_reasoning(reasoning)
        
        # 3. Visa Avrop State (v5.4, Om debug)
        if DEBUG_MODE:
            show_state(session_state, avrop_data, avrop_progress)

        # 4. Visa Svar
        console.print("\n[bold red]P-Bot:[/bold red]")
        console.print(Markdown(result.get('response', 'Inget svar.')))
        
        # 5. Visa Källor
        if result.get('sources'):
            console.print("")
            show_sources(result['sources'])

        # Uppdatera historik
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": result.get('response', '')})


def main():
    """Main entry point for CLI."""
    try:
        chat_loop()
    except KeyboardInterrupt:
        print("\nAvslutar...")


if __name__ == "__main__":
    main()
