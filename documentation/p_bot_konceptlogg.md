# P-Bot Konceptlogg (v5.27)

Detta dokument spårar "Varför" – resonemanget och de designbeslut som lett fram till prototypen.

---

## Fas 1: Initial Verksamhetsanalys & Strategisk Inramning

Projektet initierades för att lösa Addas IT-konsultupphandling som upplevdes som "komplicerad". Målet är att bygga en AI-driven "Digital Lots" (Adda Upphandlingsassistent) som levererar processtöd och mervärde.

### 1.1 Strategisk Validering (Extern Kontext)

PoC:ns syfte är att agera som en direkt teknisk implementation av Addas uttalade strategi:

- **Svara på Addas Målarkitektur:** Prototypen är designad som en frikopplad ("headless") applikation (React SPA + Python API) för att validera den MACH-arkitektur som Adda efterfrågar.

- **Adressera "Kunskapsgapet":** Adda har identifierat en central utmaning: att gå från interna AI-tester (GPTs) till robusta, externa kundlösningar. Denna PoC adresserar detta gap genom att definiera den "stateful" backend-arkitektur som krävs.

### 1.2 Målgruppshypoteser

Vi definierade två primära målgrupper:
- **"Den Ovana Beställaren":** Behöver trygghet, vägledning, "coaching".
- **"Den Erfarna Beställaren":** Behöver effektivitet, automation, "proffsverktyg".

### 1.3 Process- & Dataanalys

- **Processkarta:** Identifierade det primära vägvalet: Dynamisk Rangordning (DR) vs. Förnyad Konkurrensutsättning (FKU).
- **Kritisk Upptäckt (Regel KN5):** Identifierade en dold affärsregel: Kompetensnivå 5 (KN5) leder alltid till FKU.

---

## Fas 2: Iterativ Design (Pivots & Lösningar)

### 2.1 Pivot 1: "Den Digitala Lotsen"

**Insikt:** Processen är inte helautomatisk; den är "hybrid" och blandar digitala steg med manuella, externa steg (t.ex. "vänta på anbud").

**Konsekvens:** Tjänsten måste vara en "stateful" applikation som sparar användarens framsteg.

### 2.2 Pivot 2: "Resurs vs. Uppdrag"

**Insikt:** Vår "Ovan/Erfaren"-segmentering var felaktig. En användare som vill köpa ett "Uppdrag" (alltid FKU) ska inte tvingas igenom ett verktyg optimerat för "Resurser".

**Konsekvens:** Vi skapade "Två Stationer"-modellen:
- **Arbetsstation: Uppdrag** (FKU)
- **Arbetsstation: Resurs** (DR/FKU)

### 2.3 Pivot 3: "Det Enhetliga Flödet"

**Insikt:** Att tvinga användare att identifiera sig som "oerfarna" är psykologiskt bristfälligt.

**Konsekvens (Slutgiltig Design):** Ett enda, enhetligt "Konversationellt Flöde":
- Proffsverktyg som standard: Snabba, klickbara val
- Coachning på Begäran: Hjälp är valfri
- Valfria funktioner: Filuppladdning och kontextuella checklistor

---

## Fas 3: Bygge & Arkitektur

### 3.1 Visuell Identitet

Replikerade Addas profil:
- Primärfärg: Röd (#D32F00)
- Sekundärfärg: Petrol (#005B59)
- Typsnitt: Avenir Next / Nunito Sans
- Grid: 12-kolumns system

### 3.2 Arkitektur V5.1 (Motor/Manus-separation)

**Problem:** Prototypen var instabil (render-buggar i textanimationer).

**Lösning:**
- **Manuset:** JSON-fil (`p_bot_resource_flow.json`) definierar konversationen
- **Motorn:** React-komponent som läser JSON och renderar flödet

### 3.3 Designsystem & Komponentisering

**Insikt:** UI-konsistens var svår att upprätthålla med enbart CSS.

**Beslut:** 
- `tokens.js` som "Single Source of Truth"
- Atomär design: UI bröts ner i minsta beståndsdelar
- Designsystemet är MASTER – alla komponenter definieras där först

**Designval:**
- Visuell förenkling: Tog bort dekorativa färgade linjer
- Semantisk färgsättning: Ice Teal (aktivt), Hero Pink (arkiverat), Warm Background (användarsvar)

---

## Fas 4: AI/RAG-Backend Implementation

### 4.1 Tekniskt Beslut

**Insikt:** Prototypens simulerade AI-svar kunde inte validera den verkliga komplexiteten.

**Beslut:** Separera AI-tjänsten som fristående backend (`/ai-services`).

### 4.2 Teknisk Stack

| Komponent | Val | Motivering |
|-----------|-----|------------|
| Framework | Flask | Snabb prototyputveckling, moget AI/ML-ekosystem |
| Vektordatabas | ChromaDB | Lokal, filbaserad, ingen extern infrastruktur |
| LLM | Gemini 2.0 Flash | Hastighet och kostnadsbas för experimentering |
| Embeddings | SentenceTransformers | Lokala embeddings, minskar API-beroende |

### 4.3 Arkitektoniska Designval

- **Modularitet:** Separerade `rag_service.py` från `llm_service.py`
- **Dokumenthantering:** Stöd för PDF, DOCX, XLSX
- **Datapipeline:** `data_manager.py` för batch-inläsning
- **API-Design:** REST-principer, lätta att integrera

---

## Fas 5: AI-Driven Arkitektur (Senaste Pivot)

### 5.1 Multi-Agent System

**Insikt:** Ett enda AI-prompt fungerar inte för alla processteg.

**Beslut:** Implementera specialiserade agenter:
- INTAKE_AGENT: Behovsinsamling
- CLARIFY_AGENT: Rollbekräftelse
- LEVEL_AGENT: Kompetensbedömning
- VOLUME_AGENT: Volym och pris
- STRATEGY_AGENT: Affärsregler
- FINALIZE_AGENT: Slutförande

### 5.2 Externaliserade Promptar

**Insikt:** Hårdkodade promptar i Python-filer var svåra att underhålla.

**Beslut:** Flytta alla promptar till `config/agents.yaml`:
- Varje agent har egen `system_prompt` och `extraction_prompt`
- RAG-kategori kopplad till varje agent
- Enkel uppdatering utan koddeploy

### 5.3 Dynamisk UI

**Insikt:** Hårdkodade texter i frontend skapade inkonsistens.

**Beslut:** AI genererar allt dynamiskt:
- Meddelanden
- Input-placeholders
- Knappalternativ
- Stegövergångar

**Princip:** Frontend är en "dum" klient som bara renderar vad backend säger.

---

## Fas 6: Designsystem-omstrukturering

### 6.1 Monorepo-struktur

**Insikt:** Den stora `adda_design_system.jsx` (2100+ rader) var svår att underhålla.

**Beslut:** Dela upp i moduler:
```
design-system/
├── tokens.js
├── components/   (7 komponenter)
├── chat/         (5 komponenter)
├── layouts/      (4 komponenter)
├── list/         (1 komponent)
└── docs/         (8 dokumentationsfiler)
```

### 6.2 Design System First

**Princip:** Alla nya komponenter definieras först i designsystemet, sedan används de i applikationen.

---

## Fas 7: Session-Based Data (Deprecated)

> **OBS:** Denna fas ersattes av Fas 8 (Hjärntransplantationen). Session-based data hanteras nu av den nya Pipeline-arkitekturen.

---

## Fas 8: Hjärntransplantationen (Reasoning Engine)

### 8.1 Insikt: Hårdkodade Agenter var för Stela

**Problem:** Multi-Agent-systemet (Fas 5) med hårdkodade faser (INTAKE, CLARIFY, LEVEL, etc.) visade sig vara för stelt:

- Användaren rör sig inte linjärt genom processen
- Om användaren hoppar från steg 1 till steg 4 ("Vad kostar det?") blev den gamla motorn förvirrad
- Fas-baserad arkitektur krävde att frontend och backend var synkroniserade om "vilken fas vi är i"

**Beslut:** Implementera en "Reasoning Loop" (Plan-Execute-Evaluate) som dynamiskt anpassar sökstrategin efter frågan, inte efter vilken "vy" användaren står i.

### 8.2 Från State Machine till Pipeline

| Före (v3.x) | Efter (v4.0) |
|-------------|--------------|
| Multi-Agent med faser | 5-stegs Pipeline |
| Backend håller state | Stateless (frontend skickar historik) |
| Agenter väljs baserat på `current_phase` | Planner analyserar frågan dynamiskt |
| RAG-kategorier per agent | Dual Search (Hunter + Vector) |

### 8.3 Pipeline Architecture

```
[1] PLANNER (gemini-flash-lite)
    ↓ Analyserar frågan → sökstrategi
[2] HUNTER (exakt sökning)
    ↓ Söker nyckelord i Lake (markdown-filer)
[3] VECTOR (semantisk sökning)
    ↓ Söker i ChromaDB
[4] JUDGE (gemini-flash-lite)
    ↓ Rankar och filtrerar kandidater
[5] SYNTHESIZER (gemini-pro)
    ↓ Genererar svar från kontext
```

### 8.4 Strict Mode (Code First)

**Insikt:** AI-tolkning av prislistor och tabeller ledde till hallucinationer.

**Beslut:** Implementera "Strict Mode" med Pandas:
```python
if ext in ['.xlsx', '.xls']:
    dfs = pd.read_excel(filepath, sheet_name=None)
    for sheet, df in dfs.items():
        text += f"### Sheet: {sheet}\n{df.to_markdown(index=False)}\n\n"
```

**Säljargument:** Inga AI-hallucinationer på priser – data parsas deterministiskt.

### 8.5 OTS-Taxonomi

**Insikt:** Dokument behövde klassificeras för att förbättra sökning.

**Beslut:** Implementera OTS-taxonomi (Strategisk/Taktisk/Operativ):

| Nivå | Beskrivning | Exempel |
|------|-------------|---------|
| **STRATEGISK** | Ramverket (Lagen) | Ramavtal, Allmänna Villkor |
| **TAKTISK** | Processen (Metoden) | Avropsförfrågan, FKU, Direktavrop |
| **OPERATIV** | Objekten (Data) | Kompetensnivå, Prislista, Timpris |

### 8.6 Lake-konceptet

**Insikt:** Råfiler (PDF, XLSX) var svåra att söka i effektivt.

**Beslut:** Alla dokument konverteras till Markdown med YAML frontmatter:
```markdown
---
unit_id: "5d17edb5-..."
filename: "avropsvagledning.pdf"
graph_master_node: "Avropsvägledning"
summary: "Vägledning för avrop..."
contains_prices: false
---
[Dokumentets fulltext...]
```

### 8.7 Konsekvenser

1. **Fas-lös Backend:** AI kan svara på "Vad kostar det?" oavsett UI-steg
2. **Stateless Frontend:** Frontend skickar bara `query` + `history`
3. **Transparent Reasoning:** `thoughts` returneras för debugging
4. **Explicit Sources:** `sources` visar exakt vilka dokument som användes

---

## Fas 9: Minnesuppgraderingen (Shadow State & Intent)

### 9.1 Insikt: State Amnesia & Context Poisoning

Under testerna upptäcktes två kritiska brister i Pipeline-arkitekturen (Fas 8):

1. **State Amnesia (Minnesförlust):** När användaren definierade en roll (t.ex. "Projektledare") och sedan diskuterade en annan ("Utvecklare"), glömde botten bort den första. `extracted_entities` var platt och kunde bara hålla en uppsättning attribut.

2. **Context Poisoning (Läckage):** Vid faktafrågor ("Vad är takpriset?") hämtade botten ibland exempel från gamla avrop (ZON 2) och presenterade dem som regler.

### 9.2 Lösning: Pre-Computation Layer (Extractor)

**Beslut:** Införa ett explicit **Steg 0 (Extractor)** innan planeringen börjar.

- **Shadow State:** En JSON-struktur som håller en *lista* av resurser (`resources: []`) istället för platta fält. Detta möjliggör "Team-beställningar".
- **Intent Classification:** Extractor avgör om frågan är `FACT` eller `INSPIRATION`.

### 9.3 Lösning: Killswitch (Ghost Mode)

**Beslut:** Hårdkoda säkerhetsspärrar baserat på Intent.

- Om `Intent == FACT`: Sökning i ZON 2 (Secondary) blockeras helt.
- Om `Intent == INSPIRATION`: ZON 2 tillåts med strikta instruktioner om generalisering.

### 9.4 Lösning: Server-Driven UI (Directives)

**Insikt:** Frontend behövde gissa vilket steg processen var i.

**Beslut:** Backend styr UI explicit via `ui_directives`.

- `update_sticky_header`: Backend sätter rubriken.
- `entity_summary`: Backend renderar "varukorgen".

**Resultat:** En "Smartare" motor som minns komplexa beställningar och en "Säkrare" motor som inte hallucinerar regler från gamla exempel.

---

## Fas 10: Modular Architecture (v5.1)

### 10.1 Insikt: Monolitisk kod

`search_engine.py` hade vuxit till 500+ rader med all logik i en klass. Detta gjorde det svårt att:
- Testa enskilda komponenter
- Förstå dataflödet
- Lägga till nya funktioner utan sidoeffekter

### 10.2 Lösning: Separation of Concerns

**Beslut:** Bryta ut metoderna till specialiserade komponenter:

| Komponent | Ansvar |
|-----------|--------|
| **ExtractorComponent** | Entity extraction, state merge (anti-purge) |
| **PlannerComponent** | Query analysis, search strategy |
| **HunterComponent** | Lake search (exakt), Vector search (semantisk) |
| **SynthesizerComponent** | Response generation med fas-specifika personas |
| **Normalizer** | Entity normalization, region-mappning, KN5-validering |

### 10.3 Ny struktur

```
ai-services/
├── app/
│   ├── engine.py           # Orchestrator
│   ├── main.py             # Flask API
│   ├── components/         # Pipeline-komponenter
│   └── validators/         # Business rules
├── _archive/               # Legacy (v1-v4)
├── server.py               # Wrapper
└── search_engine.py        # Wrapper
```

### 10.4 Bakåtkompatibilitet

Wrapper-filer i roten delegerar till `app/`:
```python
# search_engine.py
from app.engine import AddaSearchEngine, engine
```

**Resultat:** Ren separation av ansvar, testbar kod, och enkel onboarding för nya utvecklare.

---

## Fas 11: Reasoning Engine v2 (Taxonomy-Aware)

### 11.1 Insikt: Planner var för enkel

**Problem:** Den gamla Planner-komponenten valde bara `target_step` och `target_type`. Den saknade:
- Djupare förståelse för dokumentens taxonomi
- Förmåga att resonera om konflikter mellan källor
- Strukturerad output för Synthesizer

### 11.2 Lösning: Intent Analyzer + Context Builder + Planner v2

**Beslut:** Dela upp Extractor/Planner i tre specialiserade komponenter:

| Komponent | Ansvar |
|-----------|--------|
| **IntentAnalyzer** | Mappar query → IntentTarget (Root, Branch, Scope, Topics) |
| **ContextBuilder** | Dual Retrieval baserat på IntentTarget (keyword + vector + graph) |
| **PlannerV2** | Resonerar om kontext, genererar ReasoningPlan |

### 11.3 IntentTarget & ReasoningPlan

**IntentTarget** (output från IntentAnalyzer):
```python
{
    "intent_category": "FACT",
    "taxonomy_roots": ["PROCESS_RULES"],
    "taxonomy_branches": ["STRATEGY", "FINANCIALS"],
    "scope_preference": "FRAMEWORK_SPECIFIC",
    "detected_topics": ["FKU", "Nivå 5"],
    "ghost_mode": True
}
```

**ReasoningPlan** (output från Planner):
```python
{
    "primary_conclusion": "Nivå 5 kräver alltid FKU enligt ramavtalet.",
    "policy_check": "Regel: KN5 → FKU (4_strategy_RULE_PRIMARY_428a5710.md)",
    "tone_instruction": "Strict/Warning",
    "conflict_resolution": None,
    "data_validation": None
}
```

### 11.4 Topic-to-Branch Inference

**Insikt:** LLM missade ofta rätt Branch (t.ex. LOCATIONS för "Stockholm").

**Lösning:** VocabularyService håller en mappning Topic→Branch. Efter LLM-svar körs inference:
```python
for topic in detected_topics:
    if topic in vocabulary["LOCATIONS"]:
        taxonomy_branches.add("LOCATIONS")
```

---

## Fas 12: Stresstestning & Discovery

### 12.1 Procurement Simulation Tool

**Syfte:** Automatisera testning av hela pipelinen med realistiska scenarion.

**Funktioner:**
- Läser `.txt`-scenarion från `test_data/scenarios/`
- AI spelar en "beställar-persona" som svarar på P-Bot
- Batch-läge för att köra alla scenarion automatiskt
- Loggar varje session till JSON

### 12.2 Persona Story Generator

**Insikt:** Checklistor och poäng ger inte insikt i upplevelsen.

**Beslut:** Låt Gemini skriva en berättelse i första person från personans perspektiv:
> *"Du vet, jag hade verkligen höga förväntningar på den där P-Bot:en... Men sen började det. Den hängde upp sig totalt. Varje gång jag sa något fick jag bara ett svar: '🛑 Åtgärd krävs: Offererad konsult måste vara på Nivå 5.' Jag fattade ju det, jag hade ju sagt det från början!"*

### 12.3 Upptäckt: "Papegoj-effekten" (Validator-loop)

**Kritisk bugg:** Vid batch-körning av 11 scenarion fastnade ALLA i oändliga loopar.

**Symptom:**
- P-Bot upprepar samma BLOCK-meddelande 15 gånger
- Användaren bekräftar kravet men botten förstår inte
- Frustration eskalerar ("JAG VET! Sluta tjata!")

**Rotorsak:** Validatorn läser constraints från SECONDARY-dokument (gamla avrop) och applicerar dem som universella regler.

### 12.4 Åtgärdsplan

| Prioritet | Åtgärd | Fil |
|-----------|--------|-----|
| P0 | Filtrera bort SECONDARY i `_load_constraints` | `normalizer.py` |
| P0 | Implementera "acknowledged constraints" i session | `engine.py` |
| P1 | Ändra nivå-krav från BLOCK till WARN | `normalizer.py` |
| P2 | Ta bort "Ingen orimlig begäran"-meddelanden | `synthesizer.py` |

---

## Fas 13: Sammanfattnings- och Upprepningsfix (v5.10)

### 13.1 Insikt: Procent-baserad logik orsakade "Papegoj-effekten"

**Problem:** Synthesizer visade sammanfattning baserat på `completion_percent >= 70%`. Detta ledde till att samma sammanfattning upprepades varje gång användaren svarade, eftersom procenten inte ändrades.

**Symptom:**
- Användaren fick samma sammanfattning 5-10 gånger
- Frustration: "Ja, jag vet! Du har redan sagt det!"
- Botten kändes "robotlik" och repetitiv

### 13.2 Lösning: Deterministisk Completion-logik

**Beslut:** Ersätt procent-baserad logik med `AvropsProgress.is_complete`:

```python
# FÖRE (v5.9)
if progress.completion_percent >= 70:
    show_summary()

# EFTER (v5.10)
if progress.is_complete:
    show_summary()
```

**Logik:**
1. `is_complete=True + bekräftelse` → Avsluta konversationen
2. `is_complete=True` → Visa sammanfattning, fråga om bekräftelse
3. `is_complete=False` → Lista saknade fält (ingen sammanfattning)

### 13.3 Insikt: Hårdkodade FKU-regler i prompt

**Problem:** `synthesizer_strategy` prompten innehöll:
```yaml
REGLER (VIKTIGT):
- Nivå 5 → FKU krävs (KN5-regeln)
- >320 timmar → FKU krävs
```

Dessa regler upprepades i varje svar, trots att de redan fanns i data lake.

### 13.4 Lösning: Ta bort hårdkodade regler

**Beslut:** Ta bort reglerna från prompten. Lägg till instruktion:
> "Förklara avropsform EN gång. Vid upprepning, referera kort: 'Som nämnt tidigare...'"

### 13.5 Resultat: Simuleringsrapport v5.10

Batch-körning av 10 scenarion visade:
- ✅ **Inga klagomål på upprepade sammanfattningar**
- ✅ **Inga klagomål på FKU-regel upprepningar**
- 🟡 Kvarstående: Begränsade viktningsval, bekräftelsefrågor, saknar personlighet

---

## Fas 14: Demo & Validering (Dec 2025)

### 14.1 Demo 2025-12-01

**Deltagare:** Adda (IT, Affärsutveckling, Kategori) + Digitalist

**Resultat:** Systemet hanterar komplexa affärsregler och logik korrekt. Demo validerade:
- ✅ Regelhantering (KN5→FKU, spärr mot blandade kompetensområden)
- ✅ Logisk validering (startdatum bakåt i tiden avvisas)

### 14.2 Identifierade Förbättringsområden

| Problem | Kategori | Beskrivning |
|---------|----------|-------------|
| **Fyrkantig guidning** | UX | Assistenten accepterar fritext istället för att guida mot Exempelroller |
| **Minnesförlust** | Logik | Glömmer takpris och andra redan angivna värden |
| **Varukorg-sync** | UI | Uppdateras inte alltid vid rolltolkning (Klick→Qlik) |
| **Geo-data fel** | Data | Härnösand kopplad till fel anbudsområde |

### 14.3 Nästa Steg

- **8/12 kl 10:** Review av justerad version
- **10/12:** Användartester

---

## Fas 15: Dict-Pipeline & SSOT (v5.24-5.25)

### 15.1 Insikt: Pydantic-modeller skapade onödig komplexitet

**Problem:** Pipeline använde Pydantic-modeller (`AvropsData`, `ReasoningPlan`, `IntentTarget`) för datatransport. Detta ledde till:
- Felmeddelanden vid typkonvertering (str→int)
- Hårdkodade enum-värden som snabbt blev föråldrade
- Svårt att följa dataflödet mellan komponenter

**Beslut:** Ta bort `app/models/` helt. Pipeline använder nu rena Python-dicts.

### 15.2 Insikt: Entity extraction i Synthesizer var fel plats

**Problem:** Synthesizer (som ska "bara svara") var också ansvarig för att extrahera entiteter. Detta bröt mot Separation of Concerns.

**Beslut:** Flytta entity extraction till Planner:
- Planner (PRO-modell) har bättre resoneringsförmåga
- Planner har tillgång till context-dokumenten för validering
- Ny regel: Extrahera ENDAST värden som FINNS i Lake

### 15.3 Lösning: AvropsContainerManager

**Insikt:** Entity-ändringar behövde en deterministisk komponent (ej LLM).

**Beslut:** Ny komponent `AvropsContainerManager`:
- Plats: `app/components/avrop_container_manager.py`
- Ansvar: Applicera ADD/UPDATE/DELETE på varukorg
- Loggar tillstånd efter varje körning
- Validerar mot kanoniska fältnamn från taxonomy

### 15.4 Insikt: Graf användes som databas (fel!)

**Problem:** Kuzu-grafen innehöll City-noder med faktisk data (stad→län→anbudsområde). Detta bröt mot SSOT-principen – samma data fanns i `geo_resolution.md`.

**Beslut:** Graf = Index, Lake = Data
- Borttagna City-noder från graf
- Graf pekar till dokument, lagrar inte data
- `geo_resolution.md` är SSOT för geografisk mappning

### 15.5 Lösning: geo_resolution Boost

**Problem:** Vektor-sökning hittade inte `geo_resolution.md` för platsfrågor.

**Beslut:** Forcera dokumentet till topp:
```python
if "LOCATIONS" in branches:
    ranked_docs = self._ensure_geo_doc(ranked_docs)
```

### 15.6 Lösning: Förenklad IntentAnalyzer

**Problem:** IntentAnalyzer-prompten var 167 rader med keyword-listor som aldrig användes av ContextBuilder.

**Beslut:** Reducera till 22 rader:
- Output: Endast `taxonomy_branches` + `search_terms`
- Borttagna: `fact_keywords`, `instruction_keywords`, `branch_patterns`

### 15.7 Konsekvenser

1. **Enklare dataflöde:** Dict in, dict ut – inga Pydantic-valideringsfel
2. **Tydligare ansvar:** Planner extraherar, Container applicerar, Synthesizer svarar
3. **SSOT:** Inga duplicerade data i graf – Lake är sanningen
4. **Robust geo-sökning:** Alltid rätt dokument för platsfrågor

---

## Lärdomar & Insikter

1. **Separation of Concerns:** Motor/Manus-separation löste render-buggar
2. **Design Tokens:** Single Source of Truth för konsistens
3. **Multi-Agent (Deprecated):** Specialiserade agenter var för stela
4. **YAML Config:** Externaliserade promptar förenklar iteration
5. **AI-Driven UI:** Låt AI generera allt dynamiskt
6. **Modularitet:** Små, fokuserade filer är lättare att underhålla
7. **Pipeline > State Machine:** Dynamisk sökstrategi slår hårdkodade faser
8. **Strict Mode:** Code First för priser och tabeller (ej AI-tolkning)
9. **OTS-Taxonomi:** Klassificering förbättrar sökprecision
10. **Shadow State:** Lista-struktur (`resources[]`) möjliggör team-beställningar
11. **Intent Classification:** FACT/INSPIRATION styr källfiltrering
12. **Killswitch (Ghost Mode):** Hårdkodade spärrar för ZON 2 vid faktafrågor
13. **UI Directives:** Backend styr frontend explicit – ingen gissning
14. **Modular Architecture:** Komponenter med tydligt ansvar förenklar underhåll
15. **State Merge (Anti-Purge):** Behåll gamla resurser även om de inte nämns igen
16. **Taxonomy-Aware Intent:** IntentAnalyzer + VocabularyService förbättrar precision
17. **ReasoningPlan:** Strukturerad output från Planner till Synthesizer
18. **Persona Stories:** Berättelser ger djupare insikt än checklistor
19. **Validator Authority Filter:** SECONDARY-regler får ALDRIG blockera
20. **Deterministisk Completion:** Använd `is_complete` istället för procent-trösklar
21. **Prompt-hygien:** Hårdkoda INTE regler i promptar – de finns i data lake
22. **Proaktiv guidning:** Användare uppskattar förslag på befintliga roller framför fritext (minskar admin)
23. **Sticky context:** Takpris och andra "globala" värden måste bevaras i session state
24. **Visual feedback:** UI-uppdateringar måste ske synkront med AI:s tolkning
25. **Dict > Pydantic:** Rena dicts är enklare för pipeline-flöden – Pydantic skapar onödig friktion
26. **SSOT:** Data ska finnas på EN plats (Lake). Index (graf/vektor) pekar till data, lagrar den inte.
27. **Entity extraction i rätt lager:** PRO-modellen (Planner) är bättre lämpad för resonerande extraktion
28. **Deterministiska komponenter:** Kritiska operationer (varukorg-ändringar) ska INTE vara LLM-baserade
29. **Forcerad context:** Vissa dokument (geo_resolution) måste alltid finnas med – vektor-sökning räcker inte
30. **Prompt-minimalism:** Färre rader = mindre förvirring för LLM. IntentAnalyzer: 167→22 rader.

---

*Version: 5.27*  
*Senast uppdaterad: 9 december 2025*  
*🧪 ANVÄNDARTEST: 10 december 2025, kl 09:00*

---

## Fas 16: Stegkrav & Determinism (v5.27)

### 16.1 Insikt: Stegprogression blockerades

**Problem:** Efter synthesizer-refaktorering slutade stegövergångar fungera:
- `WARNING - Blocked skip: step_1_intake -> step_2_level`
- Planner föreslog rätt steg men validering blockerade

**Rotorsak:** `STEP_ORDER` i planner.py innehöll både `step_1_intake` OCH `step_1_needs`:
```python
STEP_ORDER = ['step_1_intake', 'step_1_needs', 'step_2_level', ...]
```

När current_step=`step_1_intake` (index 0) och proposed_step=`step_2_level` (index 2):
- Check: `2 > 0 + 1` = True → **BLOCKERAT** (hoppade över step_1_needs)

**Lösning:** Borttagen duplicerad `step_1_needs` från STEP_ORDER.

### 16.2 Insikt: Frontend step transition notice saknades

**Problem:** Notis för "Steg 1 slutfört → Steg 2" visades inte, men "Steg 2 → Steg 3" fungerade.

**Rotorsak:** Frontend hade bara `step_1_needs` i STEP_METADATA, backend skickade `step_1_intake`:
```javascript
const STEP_METADATA = {
  step_1_needs: {...},  // ← Backend skickar step_1_intake!
  step_2_level: {...},
  ...
}
```

**Lösning:** Lade till `step_1_intake` i frontend STEP_METADATA.

### 16.3 Insikt: Synthesizer regredierade till v5.6

**Problem:** Server kraschade med `ModuleNotFoundError: No module named 'app.models'`.

**Rotorsak:** Commit 227b7c8 ("Update RAG pipeline components...") ersatte av misstag synthesizer.py v5.24 med en äldre v5.6-version som fortfarande importerade Pydantic-modeller.

**Förklaring:** Troligen AI-assistenten (Cursor) hade fel kontext och genererade gammal kod.

**Lösning:** Återställde synthesizer.py från commit 3897156 (före regressionen).

### 16.4 Fas-specifika Synthesizer-prompts

**Insikt:** En generisk synthesizer-prompt räckte inte för olika processteg.

**Beslut:** Fyra fas-specifika prompts i `assistant_prompts.yaml`:

| Prompt | Steg | Fokus |
|--------|------|-------|
| `synthesizer_step1_behov` | step_1_intake | Roller, plats, behovsbeskrivning |
| `synthesizer_step2_niva` | step_2_level | Kompetensnivå, svårighet vs pris |
| `synthesizer_step3_volym` | step_3_volume | Datum, volym, rimlighetsanalys |
| `synthesizer_step4_avslut` | step_4_strategy | Prismodell, sammanfattning |

### 16.5 SummaryCard UX-förbättringar

**Ändringar:**
- Titel: "Din Förfrågan" → "Ditt avrop"
- Fältordning: Matchar nu processens steg (beskrivning först)
- Borttagna: Räknare i header, "(X)" efter resurser

### 16.6 Start Script

**Syfte:** Förenkla uppstart av testmiljö.

**Funktioner (`start_pbot.sh`):**
1. Tar bort Kuzu-lås (`.lock`)
2. Rensar Python-cache (`__pycache__`)
3. Startar Cloudflare-tunnel (bakgrund)
4. Startar backend-server (förgrund)

---

## Lärdomar & Insikter (tillägg v5.27)

31. **Duplicerade steg-aliases:** Om samma steg har flera namn (step_1_intake/step_1_needs), välj ETT och använd konsekvent överallt.
32. **Frontend/Backend step-sync:** STEP_METADATA i frontend måste matcha backend STEP_ORDER exakt.
33. **AI-regressioner:** Vid stora ändringar, verifiera att AI-assistenten inte ersatt filer med äldre versioner.
34. **Python-cache:** `__pycache__` kan orsaka "ghost imports" efter refaktorering – rensa regelbundet.
35. **Fas-specifika prompts:** Olika processteg kräver olika ton och fokus – generiska prompts räcker inte.
