# RAG Pipeline Test (Principtest)

## Syfte
Dokumentera hur RAG-pipelinen fungerar så att felsökning kan ske snabbt utan att läsa all kod.

---

## Pipeline-översikt

```
User Query
    ↓
┌─────────────────┐
│ IntentAnalyzer  │  → Bestämmer sökstrategi (lake/vector/graph)
│ (LLM-driven)    │  → Returnerar search_terms, branches, intent
└────────┬────────┘
         ↓
┌─────────────────┐
│ ContextBuilder  │  → Hämtar dokument från ChromaDB/Lake
│                 │  → Resolvar entiteter via Kuzu-graf
│                 │     - Geo: Stad → Län → Anbudsområde
│                 │     - Alias: KN5 → Kompetensnivå 5
│                 │     - Roller: Projektledare → Kompetensområde
└────────┬────────┘
         ↓
┌─────────────────┐
│ Planner         │  → Logisk analys av kontext
│ (LLM-driven)    │  → Returnerar ReasoningPlan med tone, step, warnings
└────────┬────────┘
         ↓
┌─────────────────┐
│ Synthesizer     │  → Genererar svar
│ (LLM-driven)    │  → Extraherar entities från konversation
│                 │  → Returnerar response + avrop_changes
└────────┬────────┘
         ↓
    Response + Updated AvropsData
```

---

## Nyckelkomponenter

### 1. IntentAnalyzer
- **Fil:** `app/components/intent_analyzer.py`
- **Input:** User query, history
- **Output:** `IntentTarget` med:
  - `search_strategy`: `{lake: bool, vector: bool, graph: bool}`
  - `search_terms`: Lista med sökord
  - `detected_entities`: Lista med entiteter
  - `taxonomy_branches`: Vilka områden (ROLES, LOCATIONS, etc.)

### 2. ContextBuilder
- **Fil:** `app/components/context_builder.py`
- **Databaser:**
  - ChromaDB (`storage/index_v2/chroma`) - Vektor-sökning
  - Kuzu (`storage/index_v2/kuzu`) - Graf-relationer
  - Lake (`storage/lake_v2/*.md`) - Smart Blocks
- **Graf-resolution:** (ALLTID PÅ, oavsett search_strategy.graph)
  - `resolve_location()`: Stad → Län → Area
  - `resolve_alias()`: KN5 → Kompetensnivå 5
  - `resolve_role()`: Roll → Kompetensområde

### 3. Planner
- **Fil:** `app/components/planner.py`
- **Input:** IntentTarget, ContextResult
- **Output:** `ReasoningPlan` med:
  - `primary_conclusion`: Kärnsvaret
  - `tone_instruction`: Strict/Helpful/Informative
  - `target_step`: Vilket processteg

### 4. Synthesizer
- **Fil:** `app/components/synthesizer.py`
- **Input:** Query, ReasoningPlan, ContextResult, AvropsData, history
- **Output:** `SynthesizerResult` med:
  - `response`: Textsvar
  - `avrop_changes`: Lista med EntityChange
  - `updated_avrop`: Uppdaterad AvropsData

---

## Datamodeller

### AvropsData ("Varukorgen")
- **Fil:** `app/models/avrop.py`
- **Fält:**
  - `resources`: Lista med `Resurs` (roll, level, antal)
  - `region`: Anbudsområde A-G
  - `location_text`: Fritext plats
  - `volume`: Timmar
  - `start_date`, `end_date`: Datum
  - `takpris`: Kronor/timme
  - `prismodell`: LOPANDE, FAST_PRIS, LOPANDE_MED_TAK
  - `utvarderingsmodell`: PRIS_100, PRIS_70_KVALITET_30, etc.

### Resurs
- `roll`: Rollnamn (t.ex. "Projektledare")
- `level`: 1-5
- `antal`: Antal personer
- `is_complete`: True om roll + level är satta

---

## Förväntat data-output (Backend-first)

### Per RAG-steg

| Steg | Output | Till frontend |
|------|--------|---------------|
| IntentAnalyzer | `IntentTarget` | Nej (intern) |
| ContextBuilder | `ContextResult` | Nej (intern) |
| Planner | `ReasoningPlan` | Nej (intern) |
| Synthesizer | `SynthesizerResult` | **JA** |

### Synthesizer → Frontend

Varje request returnerar:

```json
{
  "response": "Textsvar till användaren...",
  "avrop_data": {
    "resources": [...],
    "region": "D",
    "location_text": "Stockholm",
    "anbudsomrade": "D – Stockholm",
    ...
  },
  "session_state": {...}
}
```

### AvropsData fält (backend → frontend)

**OBS:** Frontend SummaryCard måste använda EXAKT dessa fältnamn:

| Backend-fält | Typ | Exempel | SummaryCard använder |
|--------------|-----|---------|---------------------|
| `resources` | `List[Resurs]` | Se nedan | ✅ `resources` |
| `region` | `str` (enum A-G) | `"D"` | ❌ (intern) |
| `location_text` | `str` | `"Stockholm"` | ✅ `location_text` |
| `anbudsomrade` | `str` | `"D – Stockholm"` | ✅ `anbudsomrade` |
| `volume` | `int` | `160` | ✅ `volume` |
| `start_date` | `str` | `"2025-06-01"` | ✅ `start_date` |
| `takpris` | `int` | `1200` | ✅ `takpris` |

### Resurs-fält (backend → frontend)

| Backend-fält | Typ | Exempel | SummaryCard använder |
|--------------|-----|---------|---------------------|
| `id` | `str` | `"res_1"` | ✅ `id` |
| `roll` | `str` | `"Projektledare"` | ✅ `roll` |
| `level` | `int` (1-5) | `4` | ✅ `level` |
| `antal` | `int` | `1` | ✅ `antal` |
| `is_complete` | `bool` | `true` | ✅ `is_complete` |

### Villkorlig visning i SummaryCard (IMPLEMENTERAT 2025-12-05)

| Backend-fält | Visas när | Status |
|--------------|-----------|--------|
| `end_date` | Alltid (om satt) | ✅ |
| `prismodell` | `avrop_typ == FKU_*` | ✅ |
| `utvarderingsmodell` | `avrop_typ == FKU_*` | ✅ |
| `uppdragsbeskrivning` | `avrop_typ == FKU_*` | ✅ |
| `hanterar_personuppgifter` | `== true` | ✅ |
| `sakerhetsklassad` | `== true` | ✅ |
| `avrop_typ` | Alltid (om satt) | ✅ Badge i header |

### Fältnamn-mappning (löst 2025-12-05)

| LLM extraherar | Mappas till | Berikas med |
|----------------|-------------|-------------|
| `location` | `location_text` ✅ | `anbudsomrade` ✅ |

**Flöde i `_apply_changes()`:**
1. LLM extraherar `{"location": "Stockholm"}`
2. `field_mapping` konverterar: `location` → `location_text`
3. `avrop.location_text = "Stockholm"` ✅
4. Graf-lookup: `resolve_location("Stockholm")` → `{area_code: "D", area_name: "Stockholm"}`
5. `avrop.region = Region.D` ✅
6. `avrop.anbudsomrade = "D – Stockholm"` ✅ (fixat 2025-12-05)

---

## Config-filer

| Fil | Innehåll |
|-----|----------|
| `config/adda_config.yaml` | Sökvägar, modeller |
| `config/assistant_prompts.yaml` | Promptar för Planner/Synthesizer |
| `config/adda_taxonomy.json` | Anbudsområden, nivåer, kompetensområden |
| `config/learnings.json` | Geo-mappningar, alias, roller |

---

## Test-scenarion

### Test 1: Geo-resolution
```
Input: "Härnösand"
Förväntat:
  - resolve_location() returnerar: {city: "Härnösand", county: "Västernorrland", area_code: "B", area_name: "Mellersta Norrland"}
  - Synthesizer bekräftar: "Härnösand (Anbudsområde B – Mellersta Norrland)"
```

### Test 2: Alias-resolution
```
Input: "KN5"
Förväntat:
  - resolve_alias() returnerar: "Kompetensnivå 5"
  - Synthesizer extraherar: level: 5
```

### Test 3: Minnesbevarande
```
Turn 1: "Jag behöver en projektledare"
  - AvropsData.resources = [{roll: "Projektledare", level: null}]
Turn 2: "Nivå 4"
  - AvropsData.resources = [{roll: "Projektledare", level: 4}]
  - OBS: Projektledare ska finnas kvar!
```

---

## Kända problem

### 1. Alias-resolution fungerar inte alltid
- **Symptom:** `graph_resolutions.aliases = {}` trots att alias finns i grafen
- **Möjlig orsak:** Kuzu-connection stale, eller DEBUG-logg döljer fel
- **Diagnostik:** Kolla `adda_system.log` för "Alias lookup failed"

### 2. Minnesförlust mellan turns
- **Symptom:** AvropsData återställs
- **Orsak:** Frontend skickade inte tillbaka `avrop_data`
- **Fix:** Se `ResursWorkstation.jsx` - måste skicka `avrop_data` i varje request

### 3. Dubbel-resurs vid avslut (FIXAT 2025-12-05)
- **Symptom:** Vid "JA" för att bekräfta sammanfattning, addas resurser igen
- **Orsak:** LLM läste sammanfattningen och re-extraherade entities som nya ADD
- **Fix:** Tidigt return i `synthesize()` när `is_complete + user_confirming`
- **Fil:** `synthesizer.py` rad ~200-215, meddelande från `assistant_prompts.yaml`

---

## Diagnostik-kommandon

### Testa alias i graf
```bash
cd ai-services && source venvP312/bin/activate && python -c "
import kuzu
db = kuzu.Database('storage/index_v2/kuzu')
conn = kuzu.Connection(db)
result = conn.execute(\"MATCH (a:Alias {alias: 'KN5'}) RETURN a.canonical\")
print(result.get_next() if result.has_next() else 'NOT FOUND')
"
```

### Testa geo-resolution
```bash
cd ai-services && source venvP312/bin/activate && python -c "
import kuzu
db = kuzu.Database('storage/index_v2/kuzu')
conn = kuzu.Connection(db)
result = conn.execute('''
    MATCH (c:City {name: \"Härnösand\"})-[:LOCATED_IN]->(county)-[:BELONGS_TO_AREA]->(area)
    RETURN c.name, county.name, area.code, area.name
''')
print(result.get_next() if result.has_next() else 'NOT FOUND')
"
```

---

## Session Trace

### Loggfil
`logs/v2/session_trace_YYYY-MM-DD.jsonl`

### Fält per entry (uppdaterad 2025-12-05)

```json
{
  "timestamp": "...",
  "query": "user input",
  "intent": {
    "search_terms": [...],
    "search_strategy": {...}
  },
  "context": {
    "total_docs": N,
    "graph_resolutions": {...}
  },
  "session_state": {
    "resources": N,
    "entity_changes": N,
    "avrop": {
      "region": "D",
      "start_date": "2025-06-01",
      "end_date": "2025-12-31",
      "volume": 160,
      "avropsform": null,
      "prismodell": "LOPANDE",
      "utvarderingsmodell": "PRIS_70_KVALITET_30",
      "location_text": "Stockholm",
      "anbudsomrade": "D – Stockholm"
    }
  },
  "output": {
    "response_preview": "..."
  }
}
```

### Läs senaste entries
```bash
tail -5 ai-services/logs/v2/session_trace_$(date +%Y-%m-%d).jsonl | jq '.session_state.avrop'
```

---

---

## Test: Minnesbevarande (2025-12-05)

### Testscenario
```
Turn 1: "Jag behöver en projektledare" (avrop_data=None)
Turn 2: "Nivå 4" (med avrop_data från turn 1)
Turn 3: "Nivå 4" (utan avrop_data - simulerar frontend-bug)
```

### Resultat

| Turn | Input | avrop_data skickad? | Resurser i output |
|------|-------|---------------------|-------------------|
| 1 | "Jag behöver projektledare" | Nej (första turn) | 1 (Projektledare) |
| 2 | "Nivå 4" | JA | 1 (Projektledare, level 4) |
| 3 | "Nivå 4" | NEJ (simulerad bug) | 1 (Projektledare, level 4) |

### Analys

**Överraskande:** Turn 3 hade OCKSÅ 1 resurs trots att `avrop_data=None`!

**Förklaring:** Synthesizer extraherar entities från `history` (konversationshistorik), inte bara från `avrop_data`. LLM:en läser historiken och återskapar state.

**Loggen visar:**
```
Turn 3: "Added resource: Projektledare"  ← Synthesizer la till på nytt!
```

### Slutsatser

1. **Backend har "self-healing"** - kan återskapa state från history
2. **Men detta är:**
   - Ineffektivt (LLM måste tolka om varje turn)
   - Opålitligt (kan missa detaljer)
   - Fel arkitektur (frontend SKA skicka avrop_data)
3. **Frontend-fix behövs fortfarande** för robust minneshantering

### Upptäckt bugg

```
ERROR - Failed to write session trace: 'ResolvedRole' object has no attribute 'role_name'
```
→ Bugg i session trace-loggning (ResolvedRole saknar `role_name`, har bara `role`)

### Alias-resolution

**"nivå 4"** → ✅ Kuzu-graf resolvade
```
Resolved alias (case-insensitive): 'nivå 4' -> 'Kompetensnivå 4' (Begrepp)
```

**"KN5"** → ⚠️ LLM resolvade, INTE Kuzu-graf!
```
User input: "KN5"
IntentAnalyzer (LLM): search_terms=['kompetensnivå 5', 'projektledare']
ContextBuilder: 0 aliases  ← Kuzu hittade ingenting
Result: level: 5 ✓
```

**Slutsats:** IntentAnalyzer-LLM:en är smart nog att expandera "KN5" → "kompetensnivå 5" innan ContextBuilder körs. Kuzu-alias fungerar för "nivå X" men inte "KNX" i praktiken (eftersom LLM:en redan gjort jobbet).

---

## Ändringslogg

| Datum | Ändring |
|-------|---------|
| 2025-12-05 | Skapad dokumentation |
| 2025-12-05 | Lagt till minnestest-resultat |
| 2025-12-05 | KN5-test: LLM expanderar alias, Kuzu-graf ej nödvändig |
| 2025-12-05 | Kanonisk terminologi: Prompt + SummaryCard visar "Kompetensnivå X" |
| 2025-12-05 | Test kanonisk terminologi: ✅ GODKÄNT - Kuzu-alias + LLM fungerar |
| 2025-12-05 | Dokumenterat förväntade backend-fält (AvropsData → SummaryCard) |
| 2025-12-05 | FIX: `anbudsomrade` sätts nu i Synthesizer efter geo-lookup |
| 2025-12-05 | FIX: Borttagen felaktig AREA_CODE_TO_REGION mappning |
| 2025-12-05 | Dokumenterat förväntat beteende för villkorlig visning i SummaryCard |
| 2025-12-05 | IMPL: SummaryCard villkorlig visning (end_date, FKU-fält, flaggor, badge) |
| 2025-12-05 | FIX: Dubbel-resurs vid avslut - tidigt return utan LLM vid complete+confirm |
| 2025-12-05 | CONF: Lagt till static_messages i assistant_prompts.yaml (chat_start, chat_complete) |
| 2025-12-05 | FIX: Session trace saknade prismodell, utvarderingsmodell, location_text, anbudsomrade |
| 2025-12-08 | Lagt till kanonisk fältlista (börläge) |

---

## Kanonisk fältlista (Börläge 2025-12-08)

Fastlåst referens för vilka fält RAG-pipelinen ska fylla i genom konversationen.

**SSOT:** Fältdefinitionerna ska ligga i `storage/index/adda_taxonomy.json` (sektion `avrop_fields`).
Taxonomin läses av `AvropsContainer` vid startup för att validera fältnamn runtime.
Detta dokument refererar till taxonomin - taxonomin är master.

### Avrop (Globala fält)

| Fält | Typ | Beskrivning |
|------|-----|-------------|
| `resources` | `List[Resurs]` | Lista med konsulter |
| `region` | `str` (A-G) | Anbudsområde |
| `location_text` | `str` | Fritext plats |
| `anbudsomrade` | `str` | Berikad "D – Stockholm" |
| `volume` | `int` | Timmar |
| `start_date` | `str` | ISO-datum |
| `end_date` | `str` | ISO-datum |
| `takpris` | `int` | Kr/timme |
| `prismodell` | `str` | LOPANDE, FAST_PRIS, LOPANDE_MED_TAK |
| `pris_vikt` | `int` | 0-100 (%) |
| `kvalitet_vikt` | `int` | 0-100 (%) |
| `avrop_typ` | `str` | DR_RESURS, FKU_RESURS, FKU_PROJEKT |
| `uppdragsbeskrivning` | `str` | Fritext |
| `resultatbeskrivning` | `str` | Fritext |
| `godkannandevillkor` | `str` | Fritext |
| `hanterar_personuppgifter` | `bool` | Flagga |
| `sakerhetsklassad` | `bool` | Flagga |

### Resurs (Per konsult)

| Fält | Typ | Beskrivning |
|------|-----|-------------|
| `id` | `str` | Unikt ID "res_1" |
| `roll` | `str` | Rollnamn |
| `level` | `int` | 1-5 |
| `antal` | `int` | Antal personer |
| `kompetensomrade` | `str` | KO1-KO7 |
| `is_complete` | `bool` | True om roll+level satta |

---

## Planner Output (Arkitektur)

Planner är "hjärnan" som returnerar två separata outputs:

### 1. Entity Changes (Varukorg)
- **Typ:** Strukturerad lista
- **Syfte:** Uppdatera varukorgen deterministiskt
- **Används:** Alla faser
- **Format:** `[{action: "ADD", type: "resource", data: {...}}, ...]`

### 2. Strategic Input (Metadiskussion)
- **Typ:** Fritext
- **Syfte:** Förmedla P-bots kunskap/insikter till användaren
- **Används:** Fas 1 (behov) och fas 4 (strategi)
- **Injiceras:** I Synthesizer-prompten för naturlig formulering

### Varför separata?

| Aspekt | Entity Changes | Strategic Input |
|--------|----------------|-----------------|
| Karaktär | Deterministisk | Rådgivande |
| Format | JSON-struktur | Fritext |
| Mål | Fylla varukorg | Vägleda användare |
| Faser | Alla | 1 och 4 |
| Synlighet | Backend (avrop_data) | Frontend (svarstexten) |

---

## AvropsContainer (Arkitektur)

Deterministisk komponent som applicerar entity_changes på varukorgen.

### Placering i pipeline

```
1. IntentAnalyzer     (LLM)
2. ContextBuilder     (Hybrid)
3. Planner            (LLM) → entity_changes, strategic_input
4. AvropsContainer    (DETERMINISTISK) → updated_avrop
5. Synthesizer        (LLM) → response (ser uppdaterad varukorg)
```

### Fil
`app/components/avrop_container.py`

### Ansvar
- `apply(avrop, changes)` - Applicera alla ändringar
- `add_resource(avrop, resource)` - Lägg till resurs
- `remove_resource(avrop, id)` - Ta bort resurs
- `update_resource(avrop, id, field, value)` - Uppdatera resurs
- `update_global(avrop, field, value)` - Uppdatera globalt fält
- `calculate_progress(avrop)` - Beräkna hur komplett

### Karaktär
- Ingen LLM - ren Python-logik
- Enforcar kanoniska fältnamn
- Enkel att testa (unit tests)
- Loggar sitt state varje körning

