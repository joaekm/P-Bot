---
uuid: d1c24bb1-28fb-4ff8-a256-922ff49d5e6b
doc_type: smart_block
source_file: Upphandlingsdokument (GDPR).pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
- step_3_volume
- step_4_strategy
topic_tags:
- Avropsform
- Volymgräns
- Kompetensnivå
- FKU-krav
- Rollhantering
entities:
- Förnyad Konkurrensutsättning
- 320-timmarsregeln
- Nivå 5
- Egenformulerad roll
tags:
- fku
- tvingande
- 320_timmarsregeln
- nivå_5
- kn5
- egen_roll
graph_relations:
- type: TRIGGERS
  target: strategy_fku
constraints:
- param: volume_hours
  operator: GT
  value: 320
  unit: hours
  action: TRIGGER_STRATEGY_FKU
  error_msg: Volym över 320 timmar kräver Förnyad Konkurrensutsättning.
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: TRIGGER_STRATEGY_FKU
  error_msg: Nivå 5 kräver alltid Förnyad Konkurrensutsättning.
- param: role_type
  operator: EQUALS
  value: custom
  unit: null
  action: TRIGGER_STRATEGY_FKU
  error_msg: Egenformulerade roller kräver alltid Förnyad Konkurrensutsättning.
---

# Regel: Tvingande Förnyad Konkurrensutsättning (FKU)
Förnyad Konkurrensutsättning (FKU) MÅSTE användas i följande fall:
1.  **OM** uppdragets volym överstiger 320 timmar.
2.  **OM** kompetensnivå 5 (Expert) efterfrågas.
3.  **OM** en egenformulerad roll (ej från ramavtalets exempelroller) används.
4.  **OM** de tre högst rangordnade leverantörerna i en Dynamisk Rangordning inte kan leverera.