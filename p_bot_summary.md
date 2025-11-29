# P-Bot Summary (v5.0)

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

### 3.3 Adda Intelligence Engine (Backend)

```
ai-services/
├── search_engine.py      # 5-stegs Pipeline (Retrieval)
├── adda_indexer.py       # [DEPRECATED] Ersatt av data_pipeline/
├── adda_chat.py          # CLI Interface
├── data_pipeline/        # Turbo Mode Ingest (v6.5)
│   ├── start_pipeline.py # Async document processor
│   ├── config/
│   │   ├── pipeline_config.yaml
│   │   └── master_context_protocol.md
│   ├── input/
│   │   ├── primary/      # Addas huvudkällor (ZON 1)
│   │   └── secondary/    # Övrig information (ZON 2)
│   └── output/           # Smart Blocks
├── storage/
│   ├── assets/           # Råfiler (PDF, XLSX, etc.)
│   ├── lake/             # Normaliserade Markdown-filer (441 st)
│   └── index/            # ChromaDB + Kuzu Graph
└── config/
    ├── adda_config.yaml      # Systemkonfiguration
    ├── adda_taxonomy.json    # OTS-taxonomi
    └── assistant_prompts.yaml # Pipeline-promptar
```

**API Endpoints:**
| Endpoint | Metod | Beskrivning |
|----------|-------|-------------|
| `/api/conversation` | POST | Huvudendpoint för chat |
| `/api/analyze-document` | POST | Dokumentuppladdning (stub) |

### 3.4 Pipeline Architecture (6-Stegs Retrieval)

Motorn är **fas-lös** och **kontext-medveten**:

| Steg | Komponent | Modell | Ansvar |
|------|-----------|--------|--------|
| 0 | **Extractor** | gemini-flash-lite | Entity extraction + Intent-klassificering |
| 1 | **Planner** | gemini-flash-lite | Analyserar frågan, genererar sökstrategi |
| 2 | **Hunter** | – | Exakt nyckelordssökning i Lake (med authority filter) |
| 3 | **Vector** | all-MiniLM-L6-v2 | Semantisk sökning i ChromaDB (med authority filter) |
| 4 | **Judge** | gemini-flash-lite | Rankar och filtrerar kandidater |
| 5 | **Synthesizer** | gemini-pro | Genererar svar + injicerar extracted_entities |

**Intent-klassificering (Killswitch Logic):**
- `FACT` → Endast PRIMARY-källor (regler, priser) – blockerar SECONDARY
- `INSPIRATION` → Både PRIMARY och SECONDARY (hjälp, exempel)

**Strategisk fördel:** Backend är inte längre låst till "faser". Om användaren hoppar direkt till "Vad kostar det?" kan motorn svara utan att vara i rätt "fas".

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

## 8. Nyckelbegrepp (v5.0)

| Begrepp | Beskrivning |
|---------|-------------|
| **Lake** | Markdown-filer med YAML frontmatter (normaliserade dokument) |
| **Tri-Store** | Lake (Text) + Vector (Semantik) + Graph (Relationer) |
| **Process & Block Taxonomi** | step_1-4 + RULE/INSTRUCTION/DEFINITION/DATA_POINTER |
| **Extractor** | Entity extraction + Intent-klassificering (Shadow State) |
| **Killswitch (Ghost Mode)** | FACT-intent blockerar SECONDARY-källor |
| **UI Directives** | Backend-driven UI-uppdatering (entity_summary, header, step) |
| **SummaryCard** | "Varukorgen" – multi-resource beställningssammanfattning |
| **Strict Mode** | Pandas-parsing för tabeller (ej AI-hallucination) |
| **Dual Search** | Hunter (exakt) + Vector (semantisk) |

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

*Version: 5.0*  
*Status: Entity Extraction + UI Directives + Multi-Resource Support*  
*Senast uppdaterad: November 2024*
