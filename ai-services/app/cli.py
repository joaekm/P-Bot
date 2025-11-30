"""
Adda P-Bot CLI v5.2
Command-line interface for testing the search engine.

Updated to work with the new Reasoning Engine pipeline:
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
parser = argparse.ArgumentParser(description="Adda P-Bot CLI v5.2")
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
        f"[bold white]{title}[/bold white]\n[dim]Reasoning Engine v5.2[/dim]", 
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


def show_state(current_state):
    """Visa extraherade entiteter och session state."""
    if not current_state:
        return
    
    entities = current_state.get('extracted_entities', {})
    missing = current_state.get('missing_info', [])
    confidence = current_state.get('confidence', 0)
    forced_strategy = current_state.get('forced_strategy')
    
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=15)
    grid.add_column()
    
    # Confidence
    if confidence:
        grid.add_row("Confidence:", f"{confidence:.0%}")
    
    # Visa extraherade entiteter
    resources = entities.get('resources', [])
    if resources:
        res_str = ", ".join([f"{r.get('role', '?')} (L{r.get('level', '?')})" for r in resources[:3]])
        grid.add_row("Resurser:", res_str)
    
    # Global fields
    known = {k: v for k, v in entities.items() if v is not None and k != 'resources'}
    if known:
        grid.add_row("Globalt:", ", ".join([f"{k}={v}" for k, v in known.items()]))
    
    # Missing info
    if missing:
        grid.add_row("Saknas:", ", ".join(missing[:3]))
    
    # Forced strategy
    if forced_strategy:
        grid.add_row("Strategi:", f"[red]⚠️ {forced_strategy} (tvingad)[/red]")
    
    console.print(Panel(
        grid, 
        title="[bold green]📦 Session State[/bold green]", 
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

    while True:
        query = Prompt.ask("\n[bold green]Du[/bold green]")
        if query.lower() in ['exit', 'quit', 'sluta']:
            break
        if not query.strip():
            continue

        with console.status("[bold red]P-Bot resonerar...[/bold red]", spinner="dots"):
            result = engine.run(query, history, session_state)
        
        # Uppdatera session state för nästa runda
        session_state = result.get('current_state')
        ui_directives = result.get('ui_directives', {})
        reasoning = result.get('reasoning', {})
        
        # 1. Visa Intent (Om debug)
        if DEBUG_MODE:
            show_intent(ui_directives)
        
        # 2. Visa Reasoning (Om debug)
        if DEBUG_MODE:
            show_reasoning(reasoning)
        
        # 3. Visa Session State (Om debug)
        if DEBUG_MODE:
            show_state(session_state)

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
