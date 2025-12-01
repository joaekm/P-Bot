# P-Bot Summary (v5.10)

Detta dokument beskriver "Vad" – den slutgiltiga processen, designen och arkitekturstrategin.

---

## 1. Strategisk Inramning & Projektmål

Att bygga en AI-driven "Digital Lots" (Adda Upphandlingsassistent) som förenklar Addas IT-konsultupphandling.

### PoC:ns syfte är tvådelat:

**För Verksamheten (Adda):**
- Ersätta en manuell, dokumenttung process med ett guidat, kontext-medvetet digitalt flöde

**För IT (Adda):**
- Bevisa gapet "Intern GPT → Extern Lösning"
- Validera Addas MACH-Målarkitektur med headless/API-driven applikation
- **Reasoning Engine** – dynamisk sökstrategi istället för hårdkodade faser

---

## 2. Process & Design (Slutgiltig)

### 2.1 Processkarta ("Två Stationer"-modellen)

| Station | Flöde | Beskrivning |
|---------|-------|-------------|
| **Arbetsstation: Uppdrag** | FKU | För komplexa projekt/team |
| **Arbetsstation: Resurs** | DR/FKU | För enskilda konsulter |

### 2.2 Affärsregler

| Regel | Beskrivning |
|-------|-------------|
| **KN5 → FKU** | Kompetensnivå 5 tvingar fram FKU-flöde |
| **Split Deal** | Blandade nivåer kan delas upp (DR för KN1-3, FKU för KN4-5) |

### 2.3 Designmönster

**Enhetligt Konversationellt Flöde:**
- Proffsverktyg som standard (klickbara val)
- Coachning på begäran (hjälp är valfri)
- AI-driven dokumentanalys (aggressiv förifyllning)

### 2.4 Dashboard-struktur

- Tydlig uppdelning: "Resurser/Konsulter" vs "Uppdrag/Projekt"
- Listor med statusfärgkodning (Ice Teal = aktivt, Hero Pink = avslutat)
- Stateful design: Hanterar externa steg ("Väntar på anbud")

---

## 3. Arkitekturstrategi

### 3.1 Implementationsstatus

| Komponent | Status | Beskrivning |
|-----------|--------|-------------|
| **Frontend** | ✅ Implementerad | React SPA med Vite, Designsystem |
| **Backend** | ✅ Implementerad | Flask + ChromaDB + Gemini |
| **Entity Extraction** | ✅ Implementerad | Shadow State med multi-resource stöd |
| **Intent Classification** | ✅ Implementerad | FACT/INSPIRATION med Killswitch |
| **UI Directives** | ✅ Implementerad | Backend-driven UI-uppdatering |
| **Varukorgen** | ✅ Implementerad | SummaryCard med multi-resource |
| **KB1 (Fakta)** | 📝 Planerad | PostgreSQL för strukturerad data |
| **KB2 (Kontext)** | ✅ Implementerad | ChromaDB vektordatabas |

### 3.2 Frontend

```
procurement_bot/src/
├── design-system/     # MASTER - Designsystem
│   ├── tokens.js      # Design tokens
│   ├── components/    # UI-komponenter
│   ├── chat/          # Chat-komponenter
│   ├── layouts/       # Layout-komponenter
│   └── docs/          # Dokumentation
├── app/
│   └── pages/         # Sidkomponenter
└── utils/             # Hjälpfunktioner
```

**Nyckelkomponenter:**
- `ChatWindow` - Självständig chattcontainer med dynamisk header
- `SummaryCard` - "Varukorgen" för multi-resource beställningar
- `ProcessProgressBar` - Vertikal tidslinje (4 steg), driven av backend
- `ActionPanel` - Server-driven inputzon
- `SystemNotice` - Info/Success/Warning-notiser
- `AIAnswerContainer` / `UserAnswerContainer` - Pratbubblor med Markdown

### 3.3 Adda Intelligence Engine (Backend v5.2)

```
ai-services/
├── app/                      # Modulär arkitektur (v5.2)
│   ├── engine.py             # Huvudorchestrator
│   ├── main.py               # Flask API entrypoint
│   ├── cli.py                # CLI chat-verktyg
│   ├── components/           # Pipeline-komponenter
│   │   ├── extractor.py      # Entity extraction & state merge
│   │   ├── intent_analyzer.py # Query → IntentTarget (taxonomy-mappning)
│   │   ├── context_builder.py # Dual Retrieval (ersätter hunter.py)
│   │   ├── planner.py        # Reasoning → ReasoningPlan
│   │   └── synthesizer.py    # Response generation with personas
│   ├── models/               # Pydantic-modeller
│   │   ├── domain.py         # Enums (TaxonomyRoot, Branch, Scope)
│   │   └── reasoning.py      # ReasoningPlan, IntentTarget
│   ├── services/             # Runtime-tjänster
│   │   └── vocabulary_service.py  # Singleton för vocabulary.json
│   └── validators/           # Business rules
│       └── normalizer.py     # Entity normalization
├── tools/                    # Utvecklingsverktyg
│   ├── simulate_procurement.py  # Stresstestning med AI-personas
│   ├── verify_reasoning.py   # Pipeline-verifiering
│   └── output/               # Loggfiler och berättelser
├── test_data/scenarios/      # Testscenarier med personas
├── data_pipeline/            # Turbo Mode Ingest (v6.5)
├── storage/
│   ├── lake/                 # Normaliserade Markdown-filer
│   └── index/                # ChromaDB + Kuzu Graph
├── config/
│   ├── adda_config.yaml
│   ├── vocabulary.json       # Taxonomy-vokabulär
│   └── assistant_prompts.yaml
├── server.py                 # Wrapper (bakåtkompatibilitet)
└── search_engine.py          # Wrapper (bakåtkompatibilitet)
```

**Komponentansvar:**

| Komponent | Ansvar |
|-----------|--------|
| **ExtractorComponent** | Entity extraction, state merge (anti-purge) |
| **IntentAnalyzerComponent** | Query → IntentTarget (taxonomy, scope, topics) |
| **ContextBuilderComponent** | Dual Retrieval baserat på IntentTarget |
| **PlannerComponent** | Reasoning → ReasoningPlan (conclusion, policy, tone) |
| **SynthesizerComponent** | Response generation med fas-specifika personas |
| **VocabularyService** | Runtime-access till vocabulary.json |
| **Normalizer** | Entity normalization, constraint validation |

**API Endpoints:**
| Endpoint | Metod | Beskrivning |
|----------|-------|-------------|
| `/api/conversation` | POST | Huvudendpoint för chat |
| `/api/analyze-document` | POST | Dokumentuppladdning (stub) |

### 3.4 Pipeline Architecture (7-Stegs Retrieval)

Motorn är **fas-lös**, **kontext-medveten** och **taxonomy-aware**:

| Steg | Komponent | Modell | Ansvar |
|------|-----------|--------|--------|
| 0 | **Extractor** | gemini-flash-lite | Entity extraction + state merge |
| 1 | **IntentAnalyzer** | gemini-flash-lite | Query → IntentTarget (taxonomy, scope, topics) |
| 2 | **ContextBuilder** | – | Dual Retrieval (keyword + vector + graph) |
| 3 | **Planner** | gemini-flash-lite | Reasoning → ReasoningPlan |
| 4 | **Validator** | – | Constraint check (BLOCK/WARN/STRATEGY_FORCE) |
| 5 | **Synthesizer** | gemini-2.0-flash | Genererar svar med ReasoningPlan + personas |

**IntentTarget (output från steg 1):**
```python
{
    "intent_category": "FACT",           # FACT/INSPIRATION
    "taxonomy_branches": ["STRATEGY"],   # Vilka grenar att söka i
    "scope_preference": "FRAMEWORK_SPECIFIC",
    "detected_topics": ["FKU", "Nivå 5"],
    "ghost_mode": True                   # Blockera SECONDARY
}
```

**ReasoningPlan (output från steg 3):**
```python
{
    "primary_conclusion": "Nivå 5 kräver alltid FKU.",
    "policy_check": "Regel: KN5 → FKU",
    "tone_instruction": "Strict/Warning",
    "data_validation": None
}
```

**Strategisk fördel:** Taxonomy-awareness gör att sökningen träffar rätt dokument direkt. Ghost Mode blockerar SECONDARY vid faktafrågor.

---

## 4. Dataflöde

```
┌─────────────────────────────────────────┐
│           FRONTEND (React)               │
│  ResursWorkstation.jsx                   │
│  - ChatWindow + SummaryCard (Varukorgen) │
│  - ProcessProgressBar (driven av backend)│
│  - UI uppdateras via ui_directives       │
└─────────────────────────────────────────┘
         ↓ POST /api/conversation { user_message, history }
         ↑ { message, sources, thoughts, ui_directives }
┌─────────────────────────────────────────┐
│    ADDA INTELLIGENCE ENGINE (Python)     │
│  search_engine.py                        │
│  [0] Extractor (Shadow State)           │
│  [1] Planner → [2] Hunter → [3] Vector  │
│  [4] Judge → [5] Synthesizer            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   Google Gemini (multi-model)            │
│   - Pro (syntes) / Flash (analys)       │
│   - Flash-Lite (planering, extraction)  │
└─────────────────────────────────────────┘
```

### 4.1 Frontend-API Kontrakt

Frontend är **UI-driven** via `ui_directives`:
- Skickar `user_message` + `conversation_history`
- Tar emot `message` + `sources` + `thoughts` + `ui_directives`
- Uppdaterar SummaryCard, ChatWindow header, ProcessProgressBar
- Backend driver all logik – frontend renderar bara

---

## 5. Konfiguration

### 5.1 Backend (.env)
```
GOOGLE_API_KEY=din_api_nyckel
```

### 5.2 Process & Block Taxonomi [AKTIV]

> **OBS:** Den gamla OTS-taxonomin (Strategisk/Taktisk/Operativ) är ersatt av Process & Block taxonomi.

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

### 5.3 Tri-Store Architecture

| Store | Typ | Innehåll | Ansvar |
|-------|-----|----------|--------|
| **Lake** | Text (Markdown) | Sanningen | Normaliserade dokument med YAML frontmatter |
| **Vector** | Semantik | Sökbarheten | ChromaDB embeddings för semantisk sökning |
| **Graph** | Relationer | Strukturen | Kuzu graf för logik |

### 5.4 Lake-konceptet

Alla dokument konverteras till Markdown med YAML frontmatter:
```markdown
---
uuid: "5d17edb5-..."
doc_type: "smart_block"
source_file: "avropsvagledning.pdf"
authority_level: "PRIMARY"
block_type: "RULE"
process_step: ["step_2_level", "step_4_strategy"]
tags: ["kn5", "fku"]
---
[Dokumentets fulltext...]
```

---

## 6. Nästa Steg

### Prioritet 0 (Kritisk - Integration)
- [x] **Frontend-Backend Integration**: Koppla React-chatten till `/api/conversation`
- [x] **Entity Extraction**: Shadow State med multi-resource stöd
- [x] **UI Directives**: Backend-driven UI-uppdatering
- [ ] **Dokumentuppladdning**: Ingest pipeline för användarfiler

### Prioritet 1 (Hög - Funktion)
- [x] **Varukorgen (SummaryCard)**: Multi-resource beställningar
- [ ] **Strict Mode**: Pandas-parsing för prislistor (ej AI-tolkning)
- [ ] **Sources UI**: Visa källor i frontend

### Prioritet 2 (Medium)
- [x] Multi-resurs varukorg
- [ ] Split Deal-förslag
- [ ] Övriga vyer (Uppdrag, Utvärdering, Resultat)

---

## 7. Framtida Målarkitektur

### Datalager (Dubbla KB)
- **KB1 (Fakta):** PostgreSQL för strukturerad data
- **KB2 (Kontext):** ChromaDB/Pinecone för embeddings

### Integration
Integreras i Addas Optimizely-miljö som React-komponent.

---

## 8. Nyckelbegrepp (v5.2)

| Begrepp | Beskrivning |
|---------|-------------|
| **Lake** | Markdown-filer med YAML frontmatter (normaliserade dokument) |
| **Tri-Store** | Lake (Text) + Vector (Semantik) + Graph (Relationer) |
| **Process & Block Taxonomi** | step_1-4 + RULE/INSTRUCTION/DEFINITION/DATA_POINTER |
| **IntentTarget** | Output från IntentAnalyzer: taxonomy, scope, topics, ghost_mode |
| **ReasoningPlan** | Output från Planner: conclusion, policy, tone, validation |
| **Killswitch (Ghost Mode)** | FACT-intent blockerar SECONDARY-källor |
| **UI Directives** | Backend-driven UI-uppdatering (entity_summary, header, step) |
| **SummaryCard** | "Varukorgen" – multi-resource beställningssammanfattning |
| **VocabularyService** | Singleton för taxonomy-vocabulary access vid runtime |
| **Topic-to-Branch Inference** | Automatisk mappning av topics till taxonomy branches |
| **Dual Retrieval** | ContextBuilder: keyword + vector + graph sökning |

### 8.1 Testverktyg

| Verktyg | Beskrivning |
|---------|-------------|
| **simulate_procurement.py** | Stresstestning med AI-personas (batch-läge) |
| **verify_reasoning.py** | Verifiering av IntentAnalyzer + ContextBuilder |
| **Persona Story Generator** | Gemini skriver berättelser från personans perspektiv |

### Ingest Pipeline [DEPRECATED]

> **OBS:** Ersatt av Data Pipeline (Turbo Mode v6.5).

| Gammal komponent | Ersatt av |
|------------------|-----------|
| `AssetNormalizer` | UUID skapas i `start_pipeline.py` |
| `DocConverter` | `analyze_document_async()` |
| `KnowledgeBuilder` | `build_index.py` |

### Data Pipeline (Turbo Mode v6.5)

Separat bulk-ingest processor för dokumentkonvertering:

| Komponent | Funktion |
|-----------|----------|
| **AdaptiveThrottler** | Auto-scaling 1-50 concurrent, 429-hantering |
| **Washer** (gemini-flash) | Rensar metadata-brus |
| **Analyzer** (gemini-pro) | Skapar Smart Blocks |

**Dual-Zone Input:**
- **PRIMARY** (ZON 1): Addas huvudkällor – absolut vetorätt
- **SECONDARY** (ZON 2): Övrig information – bakgrundsfakta

**Block Types:**
- `RULE`: Tvingande spärrar (SKA, MÅSTE)
- `INSTRUCTION`: Steg-för-steg processer
- `DEFINITION`: Begreppsförklaringar
- `DATA_POINTER`: Pekare till extern data

---

## 9. Lösta Problem (v5.10)

### 9.1 Validator-loop ("Papegoj-effekten") ✅ LÖST

**Problem:** Validatorn läste constraints från SECONDARY-dokument och applicerade dem som universella regler.

**Lösning:** Validatorn togs bort som blockerande komponent. Constraints hanteras nu av data lake och Planner.

### 9.2 Sammanfattnings-upprepningar ✅ LÖST

**Problem:** Synthesizer visade sammanfattning baserat på procent-trösklar (70%), vilket ledde till "papegoj-effekten".

**Lösning:** Sammanfattning visas nu ENDAST när `AvropsProgress.is_complete == True`.

### 9.3 FKU-regel upprepningar ✅ LÖST

**Problem:** Hårdkodade FKU-regler i `synthesizer_strategy` prompten upprepades i varje svar.

**Lösning:** Reglerna togs bort från prompten. Ny instruktion: "Förklara avropsform EN gång."

### 9.4 Kvarstående Förbättringsområden

| Problem | Status | Beskrivning |
|---------|--------|-------------|
| Begränsade viktningsval | 🟡 Kvarstår | Användare vill ha 60/40 men får bara 50/50 eller 70/30 |
| Bekräftelsefrågor | 🟡 Kvarstår | Botten frågar om saker som redan sagts |
| Saknar personlighet | 🟡 Kvarstår | Användare önskar mer proaktiva råd |

---

*Version: 5.10*  
*Status: Reasoning Engine v2 + Taxonomy-Aware + Simulation Tool + Summary Fix*  
*Senast uppdaterad: December 2024*
