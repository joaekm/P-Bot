---
uuid: 3beabeb0-1ef6-4735-9c3c-bd92c4763021
doc_type: smart_block
source_file: avtalskort---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_2_level
- step_4_strategy
topic_tags:
- Prissättning
- Kompetensnivå
- Avropsform
- Rollbeskrivning
entities:
- Nivå 5
- Förnyad Konkurrensutsättning
tags:
- kn5
- prissättning
- fku
- egenformulerad_roll
- expert
graph_relations:
- type: TRIGGERS
  target: strategy_fku
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: TRIGGER_STRATEGY_FKU
  error_msg: Prissättning för Nivå 5 måste ske via FKU.
- param: is_custom_role
  operator: EQUALS
  value: true
  unit: null
  action: TRIGGER_STRATEGY_FKU
  error_msg: Prissättning för egenformulerad roll måste ske via FKU.
---

# Regel: Krav på FKU för prissättning av vissa roller
Prissättning MÅSTE ske via Förnyad Konkurrensutsättning (FKU) i följande fall:
1.  **Kompetensnivå 5 (Expert)**
2.  **Egenformulerade roller** (roller som inte är definierade i ramavtalet)