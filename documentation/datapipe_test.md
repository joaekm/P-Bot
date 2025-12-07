# Data Pipeline Test (Principtest)

## Syfte
Dokumentera datakällor, var de skrivs, och vad som är MASTER (single source of truth).

---

## Datakällor - Översikt

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MASTER-KÄLLOR                                │
│  (Ändras manuellt, versionshanteras, är auktoritativa)             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  config/adda_taxonomy.json     ← Anbudsområden, nivåer, kompetenser│
│  config/learnings.json         ← Geo-mappningar, alias, roller     │
│  config/assistant_prompts.yaml ← Promptar för LLM-komponenter      │
│  config/adda_config.yaml       ← Sökvägar, modeller                │
│                                                                     │
│  data_pipeline/input/primary/  ← Ramavtalsdokument (PDF/DOCX)      │
│  data_pipeline/input/secondary/← Stöddokument (FAQ, guider)        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                        adda_indexer.py
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      GENERERADE CACHER                              │
│  (Byggs om från MASTER, kan raderas och återskapas)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  storage/lake_v2/*.md          ← Smart Blocks (från primary/sec)   │
│  storage/index_v2/chroma/      ← Vektordatabas (embeddings)        │
│  storage/index_v2/kuzu/        ← Grafdatabas (relationer)          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Single Source of Truth (MASTER)

### 1. Anbudsområden (Geografiska regioner)

| Data | MASTER | Cacher | Kod som läser |
|------|--------|--------|---------------|
| Area A-G namn | `adda_taxonomy.json` | Kuzu graf | ContextBuilder |
| Län → Area mappning | `adda_taxonomy.json` | Kuzu graf | ContextBuilder |
| Kommun → Län | `learnings.json` | Kuzu graf | ContextBuilder |

**VIKTIGT:** `Region` enum i `avrop.py` måste matcha taxonomy!

```json
// adda_taxonomy.json (MASTER)
"anbudsomraden": {
  "areas": {
    "A": {"name": "Norra Norrland", "counties": ["Norrbotten", "Västerbotten"]},
    "B": {"name": "Mellersta Norrland", "counties": ["Jämtland", "Västernorrland"]},
    "C": {"name": "Norra Mellansverige", ...},
    "D": {"name": "Stockholm", "counties": ["Stockholm", "Uppsala", "Gotland"]},
    "E": {"name": "Västsverige", ...},
    "F": {"name": "Småland/Östergötland", ...},
    "G": {"name": "Sydsverige", ...}
  }
}
```

### 2. Kompetensnivåer

| Data | MASTER | Cacher | Kod som läser |
|------|--------|--------|---------------|
| Nivå 1-5 definitioner | `adda_taxonomy.json` | Lake (Smart Blocks) | Synthesizer |
| KN1-KN5 alias | `learnings.json` | Kuzu graf | ContextBuilder |

```json
// learnings.json (MASTER för alias)
{"type": "alias", "subject": "KN5", "predicate": "is_alias_for", "object": "Kompetensnivå 5"}
```

### 3. Roller och Kompetensområden

| Data | MASTER | Cacher | Kod som läser |
|------|--------|--------|---------------|
| 24 exempelroller | Primary docs | Lake (Smart Blocks) | Synthesizer |
| Roll → Kompetensområde | `learnings.json` | Kuzu graf | ContextBuilder |

### 4. Promptar

| Data | MASTER | Cacher | Kod som läser |
|------|--------|--------|---------------|
| Synthesizer-prompts | `assistant_prompts.yaml` | Ingen | Synthesizer |
| Planner-prompts | `assistant_prompts.yaml` | Ingen | Planner |

---

## Dataflöde: Indexering

```
1. adda_indexer.py körs

2. Läser MASTER-källor:
   ├── config/adda_taxonomy.json
   ├── config/learnings.json
   ├── data_pipeline/input/primary/*.pdf
   └── data_pipeline/input/secondary/*.pdf

3. Genererar Smart Blocks:
   └── storage/lake_v2/*.md

4. Bygger vektordatabas:
   └── storage/index_v2/chroma/

5. Bygger grafdatabas från learnings.json:
   └── storage/index_v2/kuzu/
       ├── City nodes (från geo-learnings)
       ├── County nodes (från taxonomy)
       ├── Area nodes (från taxonomy)
       ├── Alias nodes (från alias-learnings)
       └── Role nodes (från role-learnings)
```

---

## Kända problem: Duplicerad/konfliktande data

### Problem 1: AREA_CODE_TO_REGION (✅ LÖST 2025-12-05)

| Plats | Före | Efter |
|-------|------|-------|
| `adda_taxonomy.json` | D = Stockholm | ✅ MASTER (oförändrad) |
| `avrop.py` Region enum | D = Stockholm | ✅ Matchar |
| `synthesizer.py` | `AREA_CODE_TO_REGION["D"] → Region.A` ❌ | `Region["D"]` → `Region.D` ✅ |

**Lösning:** Borttagen `AREA_CODE_TO_REGION`. Använder `Region[area_code]` direkt.

### Problem 2: Hårdkodade mappningar i kod

**Anti-pattern:**
```python
# synthesizer.py - DÅLIGT
LOCATION_TO_REGION_FALLBACK = {
    "stockholm": Region.D,
    "göteborg": Region.E,
    ...
}
```

**Rätt approach:**
- Lägg till i `learnings.json` → indexeras till Kuzu-graf
- Kod frågar grafen, hårdkodar inte

---

## Regler för datahantering

### ✅ Rätt

1. **Ny geo-mappning behövs?**
   - Lägg till i `learnings.json`
   - Kör `adda_indexer.py`
   - Grafen uppdateras automatiskt

2. **Nytt alias behövs?**
   - Lägg till i `learnings.json`
   - Kör `adda_indexer.py`

3. **Ny prompt-text?**
   - Ändra i `assistant_prompts.yaml`
   - Starta om backend

### ❌ Fel

1. **Hårdkoda mappningar i Python-kod**
2. **Duplicera taxonomy-data i promptar**
3. **Skapa nya dict/mappningar i kod istället för config**

---

## Metod: Fylla kunskapsglapp med manuella Smart Blocks

### När ska metoden användas?

När P-Bot saknar specifik kunskap som:
- Detaljerade rollbeskrivningar
- Specifika regler som inte extraherades från dokument
- Kompletterande information som behövs för bättre svar

### Steg-för-steg

**1. Identifiera glappet**
```bash
# Sök efter vad som saknas i lake_v2
grep -r "projektledare" storage/lake_v2/ | head -5
```

**2. Skapa Smart Block med korrekt metadata**

Skapa en `.md`-fil i `storage/lake_v2/` med YAML frontmatter:

```markdown
---
uuid: roll-ko2-projektledare
doc_type: smart_block
source_file: kompetensomraden-och-exempelroller-bilaga-a.pdf
authority_level: PRIMARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- projektledare
- projektledning
- kompetensområde 2
- exempelroll
---

# Projektledare

**Kompetensområde:** 2 – Ledning och styrning

## Rollbeskrivning

En projektledare leder och ansvarar för ett i tid och 
omfattning avgränsat uppdrag.

## Efterfrågad kompetens

Projektledare ska ha kunskap om och erfarenhet av att 
strukturerat leda projekt...
```

**3. Uppdatera taxonomin (vid behov)**

Om nya kompetensområden eller roller läggs till:
```bash
# Redigera config/adda_taxonomy.json
# Lägg till nya areas, roller, etc.
```

**4. Kör omindexering**
```bash
cd ai-services
source venvP312/bin/activate
python adda_indexer.py
```

**5. Verifiera**
```bash
# Kontrollera att nya block indexerats
python -c "
import chromadb
client = chromadb.PersistentClient('storage/index_v2/chroma')
coll = client.get_collection('adda_knowledge')
results = coll.query(query_texts=['projektledare'], n_results=3)
for doc in results['documents'][0]:
    print(doc[:200])
"
```

### Filnamnskonvention

```
{phase}_{block_type}_{authority}_{beskrivning}.md

Exempel:
- 1_intake_DEFINITION_PRIMARY_roll_projektledare.md
- 4_strategy_RULE_PRIMARY_fku_regler.md
- general_FULL_DOCUMENT_PRIMARY_bilaga_a_roller.md
```

### Metadata-referens

| Fält | Värden | Beskrivning |
|------|--------|-------------|
| `authority_level` | PRIMARY, SECONDARY | PRIMARY = ramavtal, SECONDARY = stöddokument |
| `block_type` | RULE, INSTRUCTION, DEFINITION, DATA_POINTER, FULL_DOCUMENT | Typ av information |
| `taxonomy_branch` | ROLES, LOCATIONS, FINANCIALS, PROCESS, etc. | Ämneskategori |
| `scope_context` | FRAMEWORK_SPECIFIC, GENERAL_LEGAL | Specifikt för ramavtalet eller generellt |
| `suggested_phase` | step_1_intake, step_2_level, step_3_volume, step_4_strategy, general | Vilka faser blocket är relevant för |

### Exempel: Rollbeskrivningar (2025-12-07)

**Problem:** P-Bot kunde nämna roller men inte förklara efterfrågad kompetens.

**Lösning:**
1. Kopierade Bilaga A (FULL_DOCUMENT) till lake_v2
2. Skapade 24 Smart Blocks – ett per exempelroll
3. Uppdaterade `adda_taxonomy.json` med 7 kompetensområden + 24 roller
4. Körde `python adda_indexer.py`

**Resultat:** 368 block indexerade, P-Bot kan nu ge detaljerade rollbeskrivningar.

---

## Verifiering: Kontrollera datakonsistens

### Check 1: Taxonomy vs Enum
```bash
# Kolla att Region enum matchar taxonomy
python -c "
from app.models.avrop import Region
import json
with open('config/adda_taxonomy.json') as f:
    tax = json.load(f)
for code, data in tax['anbudsomraden']['areas'].items():
    enum_val = Region[code]
    print(f'{code}: Enum={enum_val.value}, Taxonomy={data[\"name\"]}')
"
```

### Check 2: Learnings i graf
```bash
# Kolla att learnings indexerats till Kuzu
python -c "
import kuzu
db = kuzu.Database('storage/index_v2/kuzu')
conn = kuzu.Connection(db)
result = conn.execute('MATCH (a:Alias) RETURN count(a)')
print(f'Alias nodes: {result.get_next()[0]}')
result = conn.execute('MATCH (c:City) RETURN count(c)')
print(f'City nodes: {result.get_next()[0]}')
"
```

---

## Ändringslogg

| Datum | Ändring |
|-------|---------|
| 2025-12-05 | Skapad dokumentation |
| 2025-12-05 | Dokumenterat AREA_CODE_TO_REGION-problemet |
| 2025-12-05 | LÖST: Borttagen AREA_CODE_TO_REGION, använder Region[area_code] |
| 2025-12-07 | Lagt till "Metod: Fylla kunskapsglapp med manuella Smart Blocks" |
| 2025-12-07 | Dokumenterat rollbeskrivnings-exemplet (24 Smart Blocks) |

