import os
import sys
import time
import yaml
import json
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Third party imports for UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import box
    from rich.text import Text
except ImportError:
    print("Rich saknas. Kör: pip install rich")
    sys.exit(1)

# --- ARGS (måste parsas FÖRE logging-konfiguration) ---
parser = argparse.ArgumentParser(description="Adda P-Bot CLI")
parser.add_argument("--debug", action="store_true", help="Visa tankeprocessen och engine-loggar")
args = parser.parse_args()

# --- LOGGING (baserat på debug-flagga) ---
DEBUG_MODE = args.debug

if DEBUG_MODE:
    # Debug mode: visa engine-loggar
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.getLogger("ADDA_ENGINE").setLevel(logging.INFO)
else:
    # Tyst läge: tysta alla loggers
    logging.basicConfig(level=logging.CRITICAL)
    logging.getLogger("ADDA_ENGINE").setLevel(logging.CRITICAL)

# Tysta alltid externa bibliotek (brus)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("httpcore").setLevel(logging.CRITICAL)
logging.getLogger("google.genai").setLevel(logging.CRITICAL)
logging.getLogger("chromadb").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Import Engine (EFTER logging är konfigurerat)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from search_engine import AddaSearchEngine

# --- CONFIG ---
def load_config():
    base_dir = Path(__file__).parent
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
    console.print(Panel(f"[bold white]{title}[/bold white]\n[dim]Tri-Store Architecture Active[/dim]", style="on red", box=box.DOUBLE, expand=False))
    if DEBUG_MODE:
        console.print("[yellow]🔧 DEBUG MODE: ON[/yellow]")

def show_thoughts(thoughts):
    if not thoughts: return
    
    # Anpassad för V6.0 Planner (Step/Type)
    step = thoughts.get('target_step', 'general')
    btype = thoughts.get('target_type', 'DEFINITION')
    reasoning = thoughts.get('reasoning', 'Ingen analys.')
    v_query = thoughts.get('vector_query', '-')

    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=15)
    grid.add_column()
    
    grid.add_row("Analys:", reasoning)
    grid.add_row("Process-steg:", f"[magenta]{step}[/magenta]")
    grid.add_row("Letar efter:", f"[yellow]{btype}[/yellow]")
    grid.add_row("Vektor-sök:", v_query)

    console.print(Panel(grid, title="[bold magenta]🧠 P-Bot Tankeprocess[/bold magenta]", border_style="magenta", expand=False))

def show_state(current_state):
    """Visa extraherade entiteter och intent"""
    if not current_state: return
    
    entities = current_state.get('extracted_entities', {})
    intent = current_state.get('current_intent', 'UNKNOWN')
    missing = current_state.get('missing_info', [])
    confidence = current_state.get('confidence', 0)
    
    grid = Table.grid(expand=True)
    grid.add_column(style="bold cyan", width=15)
    grid.add_column()
    
    grid.add_row("Intent:", f"[{'green' if intent == 'FACT' else 'yellow'}]{intent}[/]")
    grid.add_row("Confidence:", f"{confidence:.0%}")
    
    # Visa extraherade entiteter
    known = {k: v for k, v in entities.items() if v is not None}
    if known:
        grid.add_row("Känt:", ", ".join([f"{k}={v}" for k, v in known.items()]))
    if missing:
        grid.add_row("Saknas:", ", ".join(missing[:3]))  # Max 3
    
    console.print(Panel(grid, title="[bold blue]🎯 Session State[/bold blue]", border_style="blue", expand=False))

def show_sources(sources):
    if not sources: return
    
    table = Table(title="Använda Källor", box=box.SIMPLE, width=100, header_style="bold green")
    table.add_column("Filnamn", style="dim")
    # Om vi i framtiden skickar med Type/Step i sources kan vi visa det här
    
    for s in sources:
        table.add_row(s)
        
    console.print(table)

# --- MAIN LOOP ---
def chat_loop():
    show_header()
    history = [] 

    while True:
        query = Prompt.ask("\n[bold green]Du[/bold green]")
        if query.lower() in ['exit', 'quit', 'sluta']: break
        if not query.strip(): continue

        with console.status("[bold red]P-Bot resonerar...[/bold red]", spinner="dots"):
            # Kör motorn
            result = engine.run(query, history)
        
        # 1. Visa Session State (Om debug)
        if DEBUG_MODE:
            show_state(result.get('current_state'))
        
        # 2. Visa Tankar (Om debug)
        if DEBUG_MODE:
            show_thoughts(result.get('thoughts'))

        # 3. Visa Svar
        console.print("\n[bold red]P-Bot:[/bold red]")
        console.print(Markdown(result['response']))
        
        # 4. Visa Källor
        if result.get('sources'):
            console.print("")
            show_sources(result['sources'])

        # Uppdatera historik
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": result['response']})

if __name__ == "__main__":
    try:
        chat_loop()
    except KeyboardInterrupt:
        print("\nAvslutar...")
