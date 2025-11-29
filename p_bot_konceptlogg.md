# P-Bot Konceptlogg (v5.0)

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

---

*Version: 5.0*  
*Senast uppdaterad: November 2024*
