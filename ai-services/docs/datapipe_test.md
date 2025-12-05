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

