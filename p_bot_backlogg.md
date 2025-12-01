# P-Bot Backlog (v5.10)

Detta dokument spårar "Vad" och "När" – de konkreta uppgifterna fördelade på projektets faser.

---

## Fas 1: Process (Steg 1) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-101** | Definiera Målgrupp | ✅ DONE | Ovana (Coach) vs. Erfarna (Proffsverktyg). |
| **EPIC-102** | Extrahera Affärsregler | ✅ DONE | Analys av Bilagor. KN5->FKU-regeln identifierad. |
| **EPIC-103** | Validera Processkarta | ✅ DONE | Itererat till "Enhetligt Konversationellt Flöde". |

---

## Fas 2: Design (Steg 2) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-201** | Etablera Designmönster | ✅ DONE | Valde "Konversationellt Flöde". |
| **EPIC-203** | Visuell Identitet | ✅ DONE | Designsystem implementerat. |
| **EPIC-204** | Designa Layout-ramverk | ✅ DONE | 4 standardlayouter (Landing, Full, SidebarL/R). |
| **EPIC-205** | Skapa Designsystem | ✅ DONE | Atomärt Designsystem med tokens. |
| **EPIC-206** | Refaktorera Designsystem | ✅ DONE | Uppdelat i moduler (components/, chat/, layouts/, docs/). |

---

## Fas 3: Bygge av prototyp (Steg 3)

### 3a. Frontend Core ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-301** | Bygg Data-Driven Motor | ✅ DONE | JSON-driven konversationsmotor. |
| **EPIC-302** | Bygg `Arbetsstation: Resurs` | ✅ DONE | AI-driven chattarbetsstation. |
| **EPIC-307** | Bygg `Vy: Dashboard` | ✅ DONE | Hero + avropslista med ListItem. |
| **EPIC-311** | Refaktorera Chattkomponenter | ✅ DONE | ChatWindow, AIAnswerContainer, UserAnswerContainer, StepTransitionNotice. |

### 3b. Backend AI-Services

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-312** | Bygg RAG Backend | ⚠️ DEPRECATED | Ersatt av EPIC-350 Pipeline Architecture. |
| **EPIC-313** | Implementera Data Manager | ⚠️ DEPRECATED | Ersatt av EPIC-351 Ingest Pipeline. |
| **EPIC-314** | Frontend-Backend Integration | ✅ DONE | Vite proxy + fetch API. |
| **EPIC-316** | Multi-Agent System | ⚠️ DEPRECATED | Ersatt av EPIC-350 Pipeline Architecture. |
| **EPIC-317** | YAML Agent Config | ⚠️ DEPRECATED | Ersatt av EPIC-350 (promptar i YAML). |
| **EPIC-318** | AI-Driven Architecture | ⚠️ DEPRECATED | Ersatt av EPIC-350 Pipeline Architecture. |

### 3b-v2. Adda Intelligence Engine (v4.0) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-350** | Pipeline Architecture | ✅ DONE | 5-stegs retrieval (Planner→Hunter→Vector→Judge→Synthesizer). |
| **EPIC-351** | Strict Ingest Pipeline | ✅ DONE | 3-stegs ingest (AssetNormalizer→DocConverter→KnowledgeBuilder). |
| **EPIC-352** | OTS-Taxonomi | ⚠️ REPLACED | Ersatt av EPIC-366 Process & Block Taxonomi. |
| **EPIC-353** | Frontend-API Kontrakt | ✅ DONE | Stateless: query+history → response+sources+thoughts. |
| **EPIC-354** | Strict Mode | ✅ DONE | Pandas-parsing för prislistor (ej AI-tolkning). |
| **EPIC-355** | Dual Search | ✅ DONE | Hunter (exakt) + Vector (semantisk). |
| **EPIC-356** | Lake-konceptet | ✅ DONE | Markdown med YAML frontmatter. |
| **EPIC-366** | Process & Block Taxonomi | ✅ DONE | step_1-4 + RULE/INSTRUCTION/DEFINITION/DATA_POINTER. |
| **EPIC-367** | Tri-Store Architecture | ✅ DONE | Lake (Text) + Vector (Semantik) + Graph (Relationer). |

### 3b-v3. Data Pipeline (Turbo Mode v6.5) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-359** | Data Pipeline Core | ✅ DONE | Async document processor med AdaptiveThrottler. |
| **EPIC-360** | Master Context Protocol | ✅ DONE | AI-instruktioner för Smart Block-generering. |
| **EPIC-361** | Smart Block Generation | ✅ DONE | RULE, INSTRUCTION, DEFINITION, DATA_POINTER. |
| **EPIC-362** | Dual-Zone Input | ✅ DONE | PRIMARY (ZON 1) + SECONDARY (ZON 2). |
| **EPIC-363** | Adaptive Throttler | ✅ DONE | Auto-scaling 1-50 concurrent, 429-hantering. |
| **EPIC-364** | Washer + Analyzer | ✅ DONE | AI-driven metadata-rensning och blockgenerering. |
| **EPIC-365** | Multi-Format Support | ✅ DONE | PDF, DOCX, XLSX, CSV, TXT, MD. |

### 3b-v4. Smart Engine Upgrades (v5.0) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-370** | Entity Extraction (Shadow State) | ✅ DONE | Steg 0 i pipeline. Stödjer nu resource-array. |
| **EPIC-371** | Intent & Killswitch | ✅ DONE | FACT/INSPIRATION-logik för att blockera ZON 2-data. |
| **EPIC-372** | UI Directives Protocol | ✅ DONE | API-kontrakt för update_sticky_header och entity_summary. |

### 3b-v5. Modular Architecture (v5.1) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-380** | Separation of Concerns | ✅ DONE | Uppdelning i komponenter (Extractor, Planner, Hunter, Synthesizer). |
| **EPIC-381** | Validator Layer | ✅ DONE | Normalizer för entity-validering och region-mappning. |
| **EPIC-382** | Black Box Recorder | ✅ DONE | Session trace logging (JSONL). |
| **EPIC-383** | State Merge (Anti-Purge) | ✅ DONE | Förhindrar minnesförlust av resurser. |
| **EPIC-384** | Persona Switching | ✅ DONE | Fas-specifika synthesizer-promptar (intake/protocol/strategy). |
| **EPIC-385** | Legacy Archival | ✅ DONE | Gammal kod flyttad till `_archive/`. |

### 3b-v6. Reasoning Engine v2 (v5.2) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-390** | Intent Analyzer Component | ✅ DONE | Taxonomy-mappning (Root, Branch, Scope). Topic-to-Branch inference. |
| **EPIC-391** | Context Builder | ✅ DONE | Ersätter Hunter. Dual Retrieval (keyword + vector + graph). |
| **EPIC-392** | Planner v2 (Reasoning Layer) | ✅ DONE | ReasoningPlan output med conclusion, policy_check, tone. |
| **EPIC-393** | Vocabulary Service | ✅ DONE | Singleton för vocabulary.json-access vid runtime. |
| **EPIC-394** | Procurement Simulation Tool | ✅ DONE | Stresstestning med AI-personas. Batch-läge. |
| **EPIC-395** | Persona Story Generator | ✅ DONE | Gemini skriver berättelser från personans perspektiv. |

### 3b-v7. Validator Fixes ✅ LÖST

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-400** | SECONDARY Constraint Filter | ✅ DONE | Validatorn borttagen som blockerande komponent. |
| **EPIC-401** | Acknowledgement Logic | ✅ DONE | Hanteras nu av Planner med history-kontext. |
| **EPIC-402** | BLOCK → WARN Conversion | ✅ DONE | Constraints hanteras av data lake, ej kod. |
| **EPIC-403** | Remove "Rättegångskänslan" | ✅ DONE | Meddelanden borttagna. |

### 3b-v8. Summary & Repetition Fixes (v5.10) ✅

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-410** | Deterministisk Sammanfattning | ✅ DONE | Sammanfattning visas ENDAST vid `is_complete=True`. |
| **EPIC-411** | FKU-regel borttagning | ✅ DONE | Hårdkodade regler borttagna från synthesizer_strategy. |
| **EPIC-412** | Planner History Context | ✅ DONE | Planner får nu konversationshistorik för bekräftelselogik. |
| **EPIC-413** | Step Progression Validation | ✅ DONE | Planner validerar stegövergångar (ingen bakåthopp). |

### 3c. Pågående / Nästa Steg 🚩

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-308** | Varukorgsfunktion | 🚩 IN PROGRESS | Backend-stöd för multi-resurs klart. Frontend-rendering (SummaryCard) pågår. |
| **EPIC-315** | Chat-AI Integration | ✅ DONE | React-chatten kopplad till `/api/conversation`. |
| **EPIC-319** | Split Deal Logic | 📝 TO DO | Frontend-integration för blandade nivåer. |
| **EPIC-320** | Prisuppskattning | 📝 TO DO | SystemNotice med takpris efter nivåval. |
| **EPIC-321** | Session-Based Data | ⚠️ DEPRECATED | Hanteras nu av Pipeline (stateless). |
| **EPIC-322** | AgentController | ⚠️ DEPRECATED | Ersatt av Planner-steget i Pipeline. |
| **EPIC-323** | RAG Scoping | ⚠️ DEPRECATED | Ersatt av Dual Search (Hunter+Vector). |
| **EPIC-324** | Server-Driven UI | ✅ DONE | Backend styr UI via `ui_directives`. |
| **EPIC-357** | Sources UI | 📝 TO DO | Visa källor i frontend (thoughts.sources). |
| **EPIC-358** | Dokumentuppladdning | 📝 TO DO | Ingest pipeline för användarfiler. |

### 3d. Övriga Vyer 📝

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-303** | Bygg `Arbetsstation: Uppdrag` | 📝 TO DO | Skapa uppdragsflöde. |
| **EPIC-304** | Bygg `Arbetsstation: Utvärdering` | 📝 TO DO | Placeholder-vy. |
| **EPIC-305** | Bygg `Vy: Resultat (DR)` | 📝 TO DO | Placeholder-vy. |
| **EPIC-306** | Bygg `Vy: Kontrakt` | 📝 TO DO | Placeholder-vy. |
| **EPIC-310** | Städning: Teknisk Skuld | 📝 TO DO | Ta bort utfasade filer. |

---

## Fas 4: Verifiering & Rapportering (Steg 4)

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-400** | Genomför Intressent-demo (Intern) | ✅ DONE | Måndag 17/11. |
| **EPIC-401** | Genomför Användartester (Externt) | ⏳ PLANERAD | Mål: December. |
| **EPIC-402** | Leverera Slutrapport | ⏳ PLANERAD | Mål: Januari 2026. |

---

## Implementation Checklista

### Adda Intelligence Engine ✅
- [x] search_engine.py startar utan fel
- [x] ChromaDB + Kuzu initieras korrekt
- [x] Gemini API-anslutning fungerar (multi-model)
- [x] 6-stegs Pipeline implementerad (inkl. Extractor)
- [x] Dual Search (Hunter + Vector) fungerar
- [x] Process & Block Taxonomi (step_1-4 + RULE/INSTRUCTION/DEFINITION/DATA_POINTER)
- [x] Tri-Store Architecture (Lake + Vector + Graph)
- [x] Strict Mode för prislistor (Pandas)
- [x] Lake-konceptet (Markdown + YAML frontmatter)
- [x] Entity Extraction (Shadow State med multi-resource)
- [x] Intent Classification (FACT/INSPIRATION + Killswitch)

### Data Pipeline (Turbo Mode) ✅
- [x] start_pipeline.py startar utan fel
- [x] AdaptiveThrottler hanterar 429-fel
- [x] Dual-Zone input (PRIMARY/SECONDARY)
- [x] Washer rensar metadata-brus
- [x] Analyzer skapar Smart Blocks
- [x] Multi-format support (PDF, DOCX, XLSX, CSV, TXT, MD)
- [x] Master Context Protocol implementerad
- [x] 441 markdown-filer i Lake

### Frontend ✅
- [x] Vite dev-server startar
- [x] Designsystem renderar korrekt
- [x] Dashboard med Hero och ListItems
- [x] ResursWorkstation med ChatWindow
- [x] ProcessProgressBar i sidebar (backend-driven)
- [x] Sticky header visar aktuellt steg
- [x] SummaryCard (Varukorgen) med multi-resource stöd

### Integration ✅
- [x] Vite proxy vidarebefordrar `/api`
- [x] Live AI-svar i chatten (kopplad till `/api/conversation`)
- [x] UI Directives-protokoll implementerat
- [x] SummaryCard uppdateras via entity_summary
- [ ] Visa `sources` i frontend
- [ ] Dokumentuppladdning → Ingest pipeline

---

## Prioritetsordning

1. **P0 (Kritisk - Blockerare):** ✅ Alla lösta i v5.10
2. **P1 (Hög):** EPIC-357 Sources UI, EPIC-358 Dokumentuppladdning
3. **P2 (Medium):** EPIC-319 Split Deal, EPIC-320 Prisuppskattning
4. **P3 (Låg):** EPIC-303-306 Övriga vyer

### Kvarstående UX-förbättringar (Identifierade via Simulation v5.10)

| Epic-ID | Titel | Status | Kommentar |
|:--------|:------|:-------|:----------|
| **EPIC-420** | Fler viktningsalternativ | 📝 TO DO | Användare vill ha 60/40, inte bara 50/50 eller 70/30. |
| **EPIC-421** | Minska bekräftelsefrågor | 📝 TO DO | Botten frågar om saker som redan sagts. |
| **EPIC-422** | Mer konsultpersonlighet | 📝 TO DO | Proaktiva råd istället för bara alternativ. |
| **EPIC-423** | Nybörjarläge | 📝 TO DO | Förklara termer som "FKU" automatiskt. |

---

*Version: 5.10*  
*Senast uppdaterad: December 2024*
