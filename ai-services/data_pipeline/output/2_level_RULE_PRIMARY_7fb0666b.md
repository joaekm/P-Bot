---
uuid: 7fb0666b-6bea-4561-a9ee-bce0fbcceb70
doc_type: smart_block
source_file: avropsvagledning---it-konsulttjanster-2021-2025-11-21.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_2_level
- step_3_volume
- step_4_strategy
topic_tags:
- Avropsform
- Volymgräns
- Kompetensnivå
- Rollhantering
- FKU-krav
entities:
- Förnyad Konkurrensutsättning
- Nivå 5
- 320-timmarsregeln
tags:
- fku
- tvingande
- avropsstrategi
- volym
- expert
- kn5
- egen_roll
graph_relations:
- type: TRIGGERS
  target: process_fku
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
  error_msg: Kompetensnivå 5 kräver Förnyad Konkurrensutsättning.
---

# Regel: Tvingande Förnyad Konkurrensutsättning (FKU)
**OM** något av följande villkor är uppfyllt:
1.  Uppdragets totala volym **överstiger 320 timmar** (inklusive optioner).
2.  Kompetensnivå **5 (Expert)** efterfrågas.
3.  En **egenformulerad roll** (ej en av de 24 exempelrollerna) efterfrågas.

**DÅ** MÅSTE avrop ske via Förnyad Konkurrensutsättning (FKU).

**ÅTGÄRD:** Systemet SKA blockera valet av Dynamisk Rangordning och tvinga användaren till FKU-processen.