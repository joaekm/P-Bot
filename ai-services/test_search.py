import sys
import logging
import os

# Tysta loggar för testet så vi ser output tydligt
logging.basicConfig(level=logging.ERROR)

# Lägg till nuvarande mapp i sys.path för att hitta moduler
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from search_engine import engine
except ImportError:
    print("❌ Kunde inte importera 'search_engine'. Står du i 'ai-services' mappen?")
    sys.exit(1)

def main():
    # Ta fråga från argument eller kör default
    query = sys.argv[1] if len(sys.argv) > 1 else "Vad gäller för kompetensnivå 5?"
    
    print(f"\n🧠  INITIERAR SÖKNING: '{query}'\n" + "-"*40)
    
    try:
        # Kör "Hjärnan"
        result = engine.run(query)
        
        # Visa Planeringen (Debug)
        print(f"\n📋  PLANERING (Agentens tankar):")
        thoughts = result.get('thoughts', {})
        print(f"   • Jägaren letar efter: {thoughts.get('hunter_keywords')}")
        print(f"   • Vektorn söker efter: '{thoughts.get('vector_query')}'")
        print(f"   • Kriterier: {thoughts.get('ranking_criteria')}")
        
        # Visa Svaret
        print(f"\n🤖  SVAR:\n" + "-"*40)
        print(result['response'])
        print("-" * 40)
        
        # Visa Källor
        print(f"\n📚  KÄLLOR:")
        if result['sources']:
            for src in result['sources']:
                print(f"   - {src}")
        else:
            print("   (Inga källor hittades)")
            
    except Exception as e:
        print(f"\n❌ KRITISKT FEL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()