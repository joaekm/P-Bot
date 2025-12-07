# P-Bot Arkitektur (v5.15)

Detta dokument beskriver "Hur" – den tekniska implementationen av prototypen och målbilden, nu mappad mot Addas strategi.

## Bilagor

| Bilaga | Fil | Beskrivning |
|--------|-----|-------------|
| **Bilaga A** | `ragpipe_test.md` | RAG Pipeline: komponenter, dataflöde, test-scenarion, kända problem |
| **Bilaga B** | `datapipe_test.md` | Data Pipeline: MASTER-källor, var data skrivs, konsistensregler |

## 1. Omfattning

### 1.1 Strategisk Mappning
Arkitekturen är vald för att agera som en konkret implementation av Addas Målarkitektur (Bilaga 1, RFI) enligt MACH/Headless-principer.

### 1.2 Fokus
- Validera det "Konversationella Flödet" (Pivot 3)
- Hantering av affärsregler (KN5-regeln)
- AI-driven dokumentanalys och aggressiv förifyllning
- **Reasoning Engine v2** – Intent → Context → Plan → Synthesize
- **Modular Architecture** – Separation of Concerns med komponenter
- **Taxonomy-Driven Search** – Dual Retrieval baserat på IntentTarget

---

## 2. Projektstruktur

```
Adda P Bot/
├── documentation/            # Projektdokumentation
│   ├── p_bot_architecture.md # Systemarkitektur (detta dokument)
│   ├── p_bot_summary.md      # Projektöversikt och status
│   ├── p_bot_backlogg.md     # Backlogg och planerade features
│   ├── p_bot_konceptlogg.md  # Designbeslut och koncept
│   ├── ragpipe_test.md       # Bilaga A: RAG Pipeline
│   └── datapipe_test.md      # Bilaga B: Data Pipeline
│
├── procurement_bot/          # Frontend (React + Vite)
│   └── src/
│       ├── design-system/    # Designsystem (MASTER)
│       │   ├── tokens.js     # Design tokens
│       │   ├── components/   # UI-komponenter
│       │   ├── chat/         # Chat-komponenter
│       │   ├── layouts/      # Layout-komponenter
│       │   ├── list/         # List-komponenter
│       │   └── docs/         # Dokumentation (8 filer)
│       ├── app/              # Applikation
│       │   ├── Layout.jsx    # App-shell
│       │   └── pages/        # Sidkomponenter
│       └── utils/            # Hjälpfunktioner
│
├── ai-services/              # Adda Intelligence Engine v5.2
│   ├── app/                  # Modulär arkitektur (v5.2)
│   │   ├── engine.py         # Huvudorchestrator (Reasoning Engine)
│   │   ├── main.py           # Flask API entrypoint
│   │   ├── cli.py            # CLI-verktyg för testning
│   │   ├── components/       # Pipeline-komponenter
│   │   │   ├── intent_analyzer.py  # Steg 1: Query → IntentTarget
│   │   │   ├── context_builder.py  # Steg 2: Dual Retrieval
│   │   │   ├── planner.py          # Steg 3: Logik & ReasoningPlan
│   │   │   ├── synthesizer.py      # Steg 4: Response generation
│   │   │   └── extractor.py        # Legacy (state merge)
│   │   ├── models/           # Datamodeller
│   │   │   ├── domain.py     # Enums & IntentTarget
│   │   │   └── reasoning.py  # ReasoningPlan
│   │   ├── services/         # Tjänster
│   │   │   └── vocabulary_service.py  # Taxonomy lookup
│   │   └── validators/       # Business rules
│   │       └── normalizer.py # Entity normalization & constraints
│   ├── tools/                # Testverktyg
│   │   ├── verify_reasoning.py      # Pipeline-verifiering
│   │   └── simulate_procurement.py  # Stresstestning med personas
│   ├── test_data/            # Testdata
│   │   └── scenarios/        # Upphandlingsscenarier + personas
│   │       ├── NORMAL/       # Standard-scenarier (10 st)
│   │       └── HARD/         # Komplexa scenarier (5 st)
│   ├── _archive/             # Legacy-kod (v1-v4)
│   ├── config/               # Konfiguration
│   │   ├── adda_config.yaml
│   │   ├── adda_taxonomy.json  # 7 kompetensområden + 24 exempelroller
│   │   ├── assistant_prompts.yaml
│   │   └── learnings.json    # Geo-mappningar, alias, roller
│   ├── data_pipeline/        # Turbo Mode Ingest (v6.5)
│   ├── storage/              # Lake, ChromaDB, Kuzu
│   │   └── lake_v2/          # 368 Smart Blocks (inkl. rollbeskrivningar)
│   ├── server.py             # Wrapper (bakåtkompatibilitet)
│   └── search_engine.py      # Wrapper (bakåtkompatibilitet)
```

---

## 3. Frontend-Arkitektur (React)

### 3.1 Ramverk & Verktyg
- **Ramverk:** React 18 med Vite
- **Styling:** Inline styles med design tokens
- **Ikoner:** Lucide React

### 3.2 Designsystem (Single Source of Truth)

**Princip:** Alla komponenter definieras först i designsystemet (`design-system/`) innan de används i applikationen.

#### Design Tokens (`tokens.js`)
```javascript
tokens = {
  colors: {
    brand: { primary, secondary, bgHero, light, lightTint },
    neutral: { bg, text, border, surface },
    status: { info, success, warning, error + Bg/Dark varianter },
    ui: { cardBgYellow, cardBgBlue, iconBg, iconColor }
  },
  typography: { fontFamily, sizes, weights, lineHeights },
  spacing: { xs, sm, md, lg, xl, 2xl, 3xl, 4xl, 5xl, 6xl },
  borderRadius: { sm, md, lg, pill, iconCircle },
  shadows: { subtle, card, button },
  layout: { gridColumns: 12, gridGap, containerMaxWidth, breakpoints }
}
```

#### Komponentbibliotek
| Kategori | Komponenter |
|----------|-------------|
| **Core** | AddaButton, AddaCard, AddaInput, AddaTypography, SystemNotice, ProcessProgressBar, PageTitle, SummaryCard |
| **Chat** | ChatWindow, ChatAvatar, AIAnswerContainer, UserAnswerContainer, StepTransitionNotice, ActionPanel |
| **Layout** | LayoutLanding, LayoutFullWidth, LayoutSidebarLeft, LayoutSidebarRight |
| **List** | ListItem |

### 3.3 Sidstruktur

| Sida | Fil | Layout | Beskrivning |
|------|-----|--------|-------------|
| Dashboard | `Dashboard.jsx` | Landing | Startsida med hero och avropslista |
| Resurs WS | `ResursWorkstation.jsx` | SidebarRight | AI-driven chattarbetsstation |
| Uppdrag | `Uppdrag.jsx` | SidebarRight | Uppdragskonfiguration |
| DR Process | `DrProcess.jsx` | SidebarLeft | Direktavrop-process |
| FKU Process | `FkuProcess.jsx` | SidebarLeft | FKU-process |

---

## 4. Adda Intelligence Engine (Backend)

### 4.1 Teknisk Stack
- **Runtime:** Python 3.12
- **LLM Provider:** Google Gemini (multi-model)
  - `gemini-pro` – Syntes (kvalitet)
  - `gemini-flash` – Dokumentanalys (snabb)
  - `gemini-flash-lite` – Planering/logik (snabbast)
- **Vektordatabas:** ChromaDB (lokal, persistent)
- **Grafdatabas:** Kuzu (relationer mellan dokument)
- **Embeddings:** SentenceTransformer (`all-MiniLM-L6-v2`)

### 4.2 Pipeline Architecture (7-Stegs Reasoning Engine v2)

Motorn är **fas-lös** och **kontext-medveten**. Pipelinen följer flödet: **Intent → Context → Plan → Synthesize**.

| Steg | Komponent | Modell | Ansvar |
|------|-----------|--------|--------|
| 1 | **IntentAnalyzer** | gemini-flash-lite | Query → IntentTarget (taxonomy mapping) |
| 2 | **ContextBuilder** | – | Dual Retrieval (keyword + vector + graph) |
| 3 | **Planner** | gemini-flash-lite | Logik, konfliktlösning → ReasoningPlan |
| 4 | **Synthesizer** | gemini-pro | Genererar svar med persona |
| 5 | **Validator** | – | Constraint checking (data-driven) |
| 6 | **UIDirectives** | – | Backend → Frontend state updates |
| 7 | **BlackBox** | – | Session trace logging |

#### Step 1: IntentAnalyzer (Query → Taxonomy)

IntentAnalyzer mappar användarens fråga till taxonomi-koordinater:

```python
@dataclass
class IntentTarget:
    intent_category: IntentCategory  # FACT, INSPIRATION, INSTRUCTION
    detected_topics: List[str]       # ["Projektledare", "Stockholm"]
    taxonomy_branches: List[TaxonomyBranch]  # [ROLES, LOCATIONS]
    scope_preference: ScopeContext   # FRAMEWORK_SPECIFIC, GENERAL_LEGAL
    ghost_mode: bool                 # True = endast PRIMARY
    detected_entities: Dict          # Extraherade entiteter
```

**Intent-klassificering:**

| Intent | Beskrivning | Effekt |
|--------|-------------|--------|
| `FACT` | Användaren frågar om regler, priser, villkor | Ghost Mode aktivt (endast PRIMARY) |
| `INSPIRATION` | Användaren vill ha hjälp, exempel, förslag | Både PRIMARY och SECONDARY tillåts |
| `INSTRUCTION` | Användaren vill veta hur man gör | Process-fokuserad sökning |

**Topic-to-Branch Inference:**

IntentAnalyzer använder `VocabularyService` för att automatiskt mappa topics till branches:
- "Projektledare" → `ROLES`
- "Stockholm" → `LOCATIONS`
- "320 timmar" → `FINANCIALS`

#### Step 2: ContextBuilder (Dual Retrieval)

ContextBuilder ersätter den gamla Hunter-komponenten med en mer sofistikerad hämtningsstrategi:

```python
class ContextBuilder:
    def build_context(self, target: IntentTarget) -> ContextData:
        # 1. Keyword Search (exakt matchning på topic_tags)
        keyword_hits = self._search_by_keywords(target.detected_topics)
        
        # 2. Vector Search (semantisk med taxonomy-filter)
        vector_hits = self._search_vector(
            query=target.detected_topics,
            filters={
                "taxonomy_branch": target.taxonomy_branches,
                "scope_context": target.scope_preference,
                "authority_level": "PRIMARY" if target.ghost_mode else None
            }
        )
        
        # 3. Graph Traversal (Kuzu)
        graph_hits = self._traverse_graph(target.taxonomy_branches)
        
        return ContextData(
            primary_sources=...,
            secondary_sources=...,
            graph_relations=...
        )
```

#### Step 3: Planner (ReasoningPlan)

Planner analyserar kontexten och skapar en strukturerad plan:

```python
@dataclass
class ReasoningPlan:
    primary_conclusion: str      # Huvudsvar baserat på PRIMARY-källor
    policy_check: str            # Regelöverensstämmelse
    tone_instruction: str        # Persona-val (intake/protocol/strategy)
    missing_info: List[str]      # Vad saknas?
    conflict_resolution: str     # Om PRIMARY/SECONDARY motsäger varandra
    data_validation: str         # Varning om orimliga värden
    target_step: str             # step_1_intake, step_2_level, etc.
    primary_sources: List[str]   # Använda PRIMARY-källor
    secondary_sources: List[str] # Använda SECONDARY-källor
```

**Strategisk fördel:** Backend är inte längre låst till "faser". Om användaren hoppar från steg 1 till steg 4 ("Vad kostar det?") kan motorn svara direkt.

### 4.3 API Endpoints

| Endpoint | Metod | Beskrivning |
|----------|-------|-------------|
| `/api/conversation` | POST | Huvudendpoint för chat |
| `/api/analyze-document` | POST | Dokumentuppladdning (stub) |

#### Request/Response Format

**Request:**
```json
{
  "user_message": "Jag behöver en projektledare i Stockholm",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "session_state": {}
}
```

**Response:**
```json
{
  "message": "Jag noterar att du behöver en projektledare i Stockholm...",
  "sources": ["avropsvagledning.pdf", "prislista_2024.xlsx"],
  "thoughts": {
    "reasoning": "Användaren beskriver ett resursbehov",
    "target_step": "step_1_intake",
    "target_type": "DEFINITION",
    "vector_query": "projektledare konsult Stockholm"
  },
  "current_state": {
    "extracted_entities": { ... },
    "missing_info": [...],
    "current_intent": "INSPIRATION"
  },
  "ui_directives": {
    "entity_summary": {
      "resources": [...],
      "location": "Stockholm"
    },
    "update_sticky_header": "Steg 1: Beskriv Behov",
    "set_active_process_step": "step_1_intake",
    "missing_info": ["level", "volume"],
    "current_intent": "INSPIRATION"
  }
}
```

**Nyckelskillnad:** Frontend konsumerar `ui_directives` för att uppdatera UI dynamiskt utan att tolka backend-logik.

### 4.4 Tri-Store Architecture (Lake / Vector / Graph)

Systemet använder tre komplementära datalager:

| Store | Typ | Innehåll | Ansvar |
|-------|-----|----------|--------|
| **Lake** | Text (Markdown) | Sanningen | Normaliserade dokument med YAML frontmatter |
| **Vector** | Semantik | Sökbarheten | ChromaDB embeddings för semantisk sökning |
| **Graph** | Relationer | Strukturen | Kuzu graf för logik ("vilka regler gäller i steg 3?") |

#### The Lake (Normaliserade Dokument)
Alla dokument konverteras till Markdown med YAML frontmatter:

```markdown
---
uuid: "5d17edb5-6dca-4a31-963a-9dfc367f558f"
doc_type: "smart_block"
source_file: "avropsvagledning.pdf"
authority_level: "PRIMARY"
block_type: "RULE"
process_step: ["step_2_level", "step_4_strategy"]
tags: ["kn5", "fku", "tvingande"]
graph_relations: [{"type": "TRIGGERS", "target": "strategy_fku"}]
---

[Dokumentets fulltext...]
```

#### Process & Block Taxonomi (Aktiv)

**Process Steps (Graf-noder):**

| Step | Nyckelord | Beskrivning |
|------|-----------|-------------|
| `step_1_intake` | Roller, Regioner, Kravspec | Behovsanalys |
| `step_2_level` | Senioritet, Nivå 1-5, Expert | Kompetensbedömning |
| `step_3_volume` | Timpris, Takpris, 320-timmar | Volym & Pris |
| `step_4_strategy` | FKU, DR, Split Deal | Avropsstrategi |

**Block Types:**

| Typ | Nyckelord | Användning |
|-----|-----------|------------|
| `RULE` | SKA, MÅSTE, FÅR EJ | Tvingande spärrar |
| `INSTRUCTION` | Steg-för-steg | Processbeskrivningar |
| `DEFINITION` | Fakta, begrepp | Förklaringar |
| `DATA_POINTER` | Referens | Pekare till extern data |

#### Graph-komponenten (Kuzu)

Kuzu hanterar relationer som inte passar i vektorsökning:
- **Regelkopplingar:** RULE → TRIGGERS → strategy_fku
- **Process-steg:** Vilka regler aktiveras i vilket steg?
- **Beroenden:** Dokument som refererar till varandra

### 4.5 Ingest Pipeline [DEPRECATED]

> **OBS:** Denna sektion beskriver den gamla `adda_indexer.py`. Ersatt av **Data Pipeline (4.7)**.

| Gammal komponent | Ersatt av |
|------------------|-----------|
| `AssetNormalizer` | UUID skapas direkt i `start_pipeline.py` |
| `DocConverter` | `analyze_document_async()` i Data Pipeline |
| `KnowledgeBuilder` | `build_index.py` (separat indexeringsskript) |

#### Strict Mode (Code First) [Fortfarande aktivt]
För prislistor och tabeller används **Pandas-parsing** istället för AI-tolkning:
```python
if ext in ['.xlsx', '.xls']:
    dfs = pd.read_excel(filepath, sheet_name=None)
    for sheet, df in dfs.items():
        text += f"### Sheet: {sheet}\n{df.to_markdown(index=False)}\n\n"
```

**Säljargument:** Inga AI-hallucinationer på priser – data parsas deterministiskt.

### 4.7 Data Pipeline (Turbo Mode Ingest v6.5)

`data_pipeline/start_pipeline.py` är en separat, asynkron dokumentprocessor för bulk-ingest:

```
data_pipeline/
├── start_pipeline.py          # Turbo Mode Processor
├── config/
│   ├── pipeline_config.yaml   # Systemkonfiguration
│   └── master_context_protocol.md  # AI-instruktioner
├── input/
│   ├── primary/               # Addas huvudkällor (ZON 1)
│   └── secondary/             # Övrig information (ZON 2)
├── output/                    # Smart Blocks (mellanlandning)
└── output_archive/            # Processade originalfiler
```

#### Adaptive Throttler (429-hantering)

Pipelinen har en intelligent hastighetsregulator:

| Parameter | Värde | Beskrivning |
|-----------|-------|-------------|
| **Initial Concurrency** | 5 | Startpunkt för parallella requests |
| **Max Concurrency** | 50 | Maximal parallellitet |
| **Min Concurrency** | 1 | Fallback vid hög belastning |
| **Brake Factor** | 0.5 | Halverar vid 429-fel |
| **Cooldown** | 10s | Paus efter bromsning |

#### Dual-Zone Input (Authority Levels)

| Zon | Mapp | Auktoritet | Behandling |
|-----|------|------------|------------|
| **PRIMARY** | `input/primary/` | Absolut vetorätt | Strikta instruktioner |
| **SECONDARY** | `input/secondary/` | Bakgrundsfakta | Sammanfattade principer |

#### AI-Driven Processing

| Steg | Modell | Funktion |
|------|--------|----------|
| **Washer** | gemini-flash | Rensar metadata-brus (sidhuvuden, sidnummer) |
| **Analyzer** | gemini-pro | Skapar Smart Blocks med process_step-taggning |

#### Smart Block Output

Varje dokument genererar:
1. **Full Document Reference** – Hela den tvättade texten
2. **Smart Blocks** – Atomära kunskapsblock med metadata

```markdown
---
uuid: "abc123..."
doc_type: "smart_block"
source_file: "avropsvagledning.pdf"
authority_level: "PRIMARY"
block_type: "RULE"
process_step: ["step_2_level", "step_4_strategy"]
tags: ["kn5", "fku", "tvingande"]
graph_relations: [{"type": "TRIGGERS", "target": "strategy_fku"}]
---

# Regel: Krav på FKU vid Nivå 5
**OM** vald nivå är 5 (Expert):
**DÅ** MÅSTE strategin vara FKU.
```

#### Block Types (Taxonomi)

| Typ | Nyckelord | Beskrivning |
|-----|-----------|-------------|
| **RULE** | SKA, MÅSTE, FÅR EJ | Tvingande spärrar |
| **INSTRUCTION** | Steg-för-steg | Processbeskrivningar |
| **DEFINITION** | Fakta | Begreppsförklaringar |
| **DATA_POINTER** | Referens | Pekare till extern data |

#### Process Steps (Graf-noder)

| Step | Nyckelord |
|------|-----------|
| `step_1_intake` | Roller, Regioner, Kravspecifikation |
| `step_2_level` | Senioritet, Nivå 1-5, Expert |
| `step_3_volume` | Timpris, Takpris, 320-timmarsregeln |
| `step_4_strategy` | FKU, DR, Split Deal, Avropsform |

#### Format Support

| Format | Hantering |
|--------|-----------|
| PDF | `pypdf.PdfReader` |
| DOCX | `python-docx` |
| XLSX/XLS | `pandas.read_excel` → Markdown-tabell |
| CSV | `pandas.read_csv` → Markdown-tabell |
| TXT/MD | Direkt läsning |

### 4.6 Session State & UI Directives

Backend skickar strukturerad data till frontend via `ui_directives` för att driva UI-uppdateringar.

#### UI Directives Object

| Fält | Typ | Beskrivning |
|------|-----|-------------|
| `entity_summary` | Object | Extraherade entiteter (multi-resource format) |
| `update_sticky_header` | String | Titel för ChatWindow header |
| `set_active_process_step` | String | Aktivt steg för ProcessProgressBar |
| `missing_info` | Array | Lista på saknad information |
| `current_intent` | String | "FACT" eller "INSPIRATION" |

#### Multi-Resource Entity Format

Stödjer team-beställningar med flera resurser:

```json
{
  "resources": [
    { "id": "res_1", "role": "Projektledare", "level": 4, "quantity": 1, "status": "DONE" },
    { "id": "res_2", "role": "Utvecklare", "level": null, "quantity": 2, "status": "PENDING" }
  ],
  "location": "Stockholm",
  "volume": "500 timmar",
  "start_date": "2025-06-01",
  "price_cap": null
}
```

| Fält | Scope | Beskrivning |
|------|-------|-------------|
| `resources` | Per-resurs | Lista med roller, nivåer, status |
| `location` | Global | Plats för hela avropet |
| `volume` | Global | Total volym i timmar |
| `start_date` | Global | Önskat startdatum |
| `price_cap` | Global | Takpris/budget |

**Status-logik:**
- `DONE` = Både roll OCH nivå är specificerade
- `PENDING` = Nivå saknas (behöver frågas)

#### Frontend-konsumtion

`ResursWorkstation.jsx` hanterar UI Directives:

```javascript
// State-variabler
const [summaryData, setSummaryData] = useState({});
const [headerTitle, setHeaderTitle] = useState('Resursupphandling');
const [activeStep, setActiveStep] = useState('step_1_needs');

// I handleAIResponse:
if (data.ui_directives) {
  setSummaryData(data.ui_directives.entity_summary);
  setHeaderTitle(data.ui_directives.update_sticky_header);
  setActiveStep(data.ui_directives.set_active_process_step);
}
```

**Kopplingar:**
- `SummaryCard.data` ← `summaryData`
- `ChatWindow.currentStepTitle` ← `headerTitle`
- `ProcessProgressBar.currentStepIndex` ← `activeStep` (mappat)

### 4.7 Dual Search (Hunter + Vector)

Motorn kombinerar två sökstrategier:

| Strategi | Typ | Användning |
|----------|-----|------------|
| **Hunter** | Exakt nyckelord | "KN5", "Bör-krav", "Allmänna villkor" |
| **Vector** | Semantisk | "senior projektledare" → "Ledning och Styrning nivå 4" |

Planner bestämmer vilka nyckelord som går till Hunter respektive Vector baserat på frågan.

---

## 5. Dataflöde

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ResursWorkstation.jsx                                  │ │
│  │  - ChatWindow (sticky header, scrollbar meddelanden)   │ │
│  │  - SummaryCard ("Varukorgen" - multi-resource)         │ │
│  │  - ProcessProgressBar (sidebar, driven av activeStep)  │ │
│  │  - ActionPanel (input zone)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│         ↓ POST /api/conversation { user_message, history }  │
│         ↑ { message, sources, thoughts, ui_directives }     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│            ADDA INTELLIGENCE ENGINE (Python)                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  search_engine.py - AddaSearchEngine.run()             │ │
│  └────────────────────────────────────────────────────────┘ │
│         │                                                    │
│         ├─→ [0] EXTRACTOR (gemini-flash-lite)              │
│         │       Entity extraction + Intent-klassificering   │
│         │       → current_state (Shadow State)              │
│         │       → Killswitch: FACT → PRIMARY only           │
│         │                                                    │
│         ├─→ [1] PLANNER (gemini-flash-lite)                 │
│         │       Analyserar frågan → sökstrategi             │
│         │                                                    │
│         ├─→ [2] HUNTER (exakt sökning)                      │
│         │       Söker i Lake (med authority filter)         │
│         │                                                    │
│         ├─→ [3] VECTOR (semantisk sökning)                  │
│         │       Söker i ChromaDB (med authority filter)     │
│         │                                                    │
│         ├─→ [4] JUDGE (gemini-flash-lite)                   │
│         │       Rankar och filtrerar kandidater             │
│         │                                                    │
│         └─→ [5] SYNTHESIZER (gemini-pro)                    │
│                 Genererar svar + injicerar extracted_entities│
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  storage/                                               │ │
│  │  ├── lake/     → Markdown med YAML frontmatter         │ │
│  │  └── index/    → ChromaDB + Kuzu Graph                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 5.1 Frontend-API Kontrakt

Frontend är **UI-driven** via `ui_directives`:
- Skickar `user_message` + `conversation_history`
- Tar emot `message` + `sources` + `thoughts` + `ui_directives`
- Uppdaterar SummaryCard, ChatWindow header, ProcessProgressBar baserat på directives
- Håller ingen state åt backend – all logik i backend

---

## 6. Affärsregler (Implementerade)

### 6.1 KN5 → FKU-regeln
```
OM minst en resurs har kompetensnivå KN5
DÅ måste hela avropet ske via Förnyad Konkurrensutsättning (FKU)
```

### 6.2 Split Deal Optimization
```
OM varukorgen innehåller blandade nivåer (KN1-3 + KN4-5)
DÅ föreslå uppdelning:
  - DR för KN1-3 resurser
  - FKU för KN4-5 resurser
```

---

## 7. Konfiguration

### 7.1 Miljövariabler (`ai-services/.env`)
```
GOOGLE_API_KEY=din_api_nyckel
```

### 7.2 Vite Proxy (`procurement_bot/vite.config.js`)
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:5000'
  }
}
```

---

## 8. Framtida Målarkitektur

### 8.1 Datalager (Dubbla KB)
- **KB1 (Fakta):** PostgreSQL för strukturerad data (roller, priser, regler, användarstate)
- **KB2 (Kontext):** ChromaDB/Pinecone för ostrukturerad text och embeddings

### 8.2 Integration
Integreras i Addas Optimizely-miljö som React-komponent som anropar Python API.

### 8.3 Session-Based Data (Planerad)

För användaruppladdade dokument:

| Typ | Lagring | Innehåll |
|-----|---------|----------|
| **Session-Based (Private)** | Frontend state | Uppladdade filer |
| **Global Knowledge (Public)** | ChromaDB | Regler, nivådefinitioner |

**Princip:** Användardata indexeras ALDRIG i vektordatabasen.

---

## 9. Modular Architecture (v5.2)

### 9.1 Komponentstruktur

Backend är nu uppdelad i specialiserade komponenter enligt "Separation of Concerns":

| Komponent | Fil | Ansvar |
|-----------|-----|--------|
| **IntentAnalyzerComponent** | `app/components/intent_analyzer.py` | Query → IntentTarget (taxonomy mapping) |
| **ContextBuilderComponent** | `app/components/context_builder.py` | Dual Retrieval (keyword + vector + graph) |
| **PlannerComponent** | `app/components/planner.py` | Logik, konfliktlösning → ReasoningPlan |
| **SynthesizerComponent** | `app/components/synthesizer.py` | Response generation, personas |
| **ExtractorComponent** | `app/components/extractor.py` | Legacy: Entity extraction, state merge |
| **ConstraintValidator** | `app/validators/normalizer.py` | Data-driven constraint validation |
| **VocabularyService** | `app/services/vocabulary_service.py` | Taxonomy lookup (singleton) |

### 9.2 Modeller

| Modell | Fil | Beskrivning |
|--------|-----|-------------|
| **IntentTarget** | `app/models/domain.py` | Taxonomy-koordinater för sökning |
| **ReasoningPlan** | `app/models/reasoning.py` | Strukturerad plan från Planner |
| **TaxonomyRoot** | `app/models/domain.py` | Enum: PROCESS, DOMAIN_OBJECTS, ARTIFACTS |
| **TaxonomyBranch** | `app/models/domain.py` | Enum: ROLES, LOCATIONS, FINANCIALS, etc. |
| **ScopeContext** | `app/models/domain.py` | Enum: FRAMEWORK_SPECIFIC, GENERAL_LEGAL |

### 9.3 Pipeline-flöde (v5.2)

```
[1] IntentAnalyzer.analyze()    → Query → IntentTarget
[2] ContextBuilder.build()      → Dual Retrieval → ContextData
[3] Planner.create_plan()       → Logik → ReasoningPlan
[4] Synthesizer.synthesize()    → Generera svar med persona
[5] Validator.validate()        → Constraint checking
[6] UIDirectives                → Backend → Frontend state
[7] BlackBox.log()              → Session trace
```

### 9.4 Bakåtkompatibilitet

Wrapper-filer i roten säkerställer att befintlig kod fungerar:

```python
# search_engine.py (wrapper)
from app.engine import AddaSearchEngine, engine

# server.py (wrapper)
from app.main import app, main
```

---

## 10. Testverktyg

### 10.1 Procurement Simulation Tool

`tools/simulate_procurement.py` är ett stresstestverktyg för att validera Reasoning Engine:

```bash
# Kör batch-simulering av alla scenarier
python tools/simulate_procurement.py --batch

# Kör enskilt scenario
python tools/simulate_procurement.py
```

**Funktionalitet:**
- Läser scenarier från `test_data/scenarios/`
- Genererar AI-personas som spelar beställare
- Kör multi-turn konversationer (max 15 rundor)
- Sparar detaljerade loggar i `tools/output/`
- Genererar "Persona Stories" – narrativa berättelser om upplevelsen

### 10.2 Verification Script

`tools/verify_reasoning.py` testar pipeline-komponenterna isolerat:

```bash
python tools/verify_reasoning.py
```

**Testar:**
- IntentAnalyzer: Korrekt taxonomy-mappning
- ContextBuilder: Dual Retrieval-resultat
- Planner: ReasoningPlan-generering

---

## 11. Kända Problem

### 11.1 Validator-Loop ("Papegoj-effekten") ✅ LÖST

**Problem:** `ConstraintValidator` laddade constraints från ALLA markdown-filer, inklusive `SECONDARY`-dokument.

**Lösning (v5.10):** Validatorn har tagits bort som blockerande komponent. Constraints hanteras nu av data lake och Planner.

### 11.2 Sammanfattnings-upprepningar ✅ LÖST (v5.10)

**Problem:** Synthesizer visade sammanfattning baserat på `completion_percent >= 70%`, vilket ledde till att samma sammanfattning upprepades gång på gång.

**Lösning:** Sammanfattning visas nu ENDAST när `AvropsProgress.is_complete == True`:
- `is_complete=True + bekräftelse` → Avsluta konversationen
- `is_complete=True` → Visa sammanfattning, fråga om bekräftelse
- `is_complete=False` → Lista saknade fält (ingen sammanfattning)

### 11.3 FKU-regel upprepningar ✅ LÖST (v5.10)

**Problem:** `synthesizer_strategy` prompten innehöll hårdkodade FKU-regler som upprepades i varje svar.

**Lösning:** Reglerna togs bort från prompten (de finns redan i data lake). Ny instruktion: "Förklara avropsform EN gång. Vid upprepning, referera kort."

---

## 12. Teknisk Dokumentation

För detaljerade test-scenarion och diagnostik, se:

| Bilaga | Fil | Syfte |
|--------|-----|-------|
| **Bilaga A** | `ragpipe_test.md` | RAG Pipeline: komponenter, dataflöde, test-scenarion, kända problem |
| **Bilaga B** | `datapipe_test.md` | Data Pipeline: MASTER-källor, var data skrivs, konsistensregler |

Alla dokument finns i `documentation/`-mappen i projektroten.

---

*Version: 5.15*  
*Senast uppdaterad: 7 december 2025*
