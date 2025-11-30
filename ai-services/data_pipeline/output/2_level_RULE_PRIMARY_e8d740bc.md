---
uuid: e8d740bc-5af2-4155-a6e9-76fce14ddab0
doc_type: smart_block
source_file: efterfragat-resursbehov-bilaga-b-dynamisk-rangordning---it-konsulttjanster-2021-v4.0-2022-11-21.xlsx
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_2_level
- step_4_strategy
topic_tags:
- Kompetensnivå
- Avropsform
- FKU-krav
entities:
- KN5
- Kompetensnivå 5
- Förnyad Konkurrensutsättning
- Dynamisk Rangordning
- IT-konsulttjänster 2021
tags:
- kn5
- fku
- tvingande
- regel
- avropsform
graph_relations:
- type: REQUIRES
  target: strategy_fku
  condition: competence_level == 5
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: TRIGGER_STRATEGY_FKU
  error_msg: Kompetensnivå 5 kräver alltid Förnyad Konkurrensutsättning (FKU).
---

# Regel: Obligatorisk FKU för Kompetensnivå 5
**OM** Kompetensnivå 5 (KN5) efterfrågas:
**DÅ** MÅSTE avropsformen vara Förnyad Konkurrensutsättning (FKU).

**KONTROLL:** Systemet ska blockera valet av Dynamisk Rangordning för KN5.