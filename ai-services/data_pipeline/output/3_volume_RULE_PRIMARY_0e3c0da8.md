---
uuid: 0e3c0da8-7707-455b-930f-f279be6397c4
doc_type: smart_block
source_file: avtalskort---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Avropsform
- Volymgräns
- Tidsgräns
entities:
- 320-timmarsregeln
- Dynamisk Rangordning
- Förnyad Konkurrensutsättning
tags:
- 320h_regeln
- fku
- dynamisk_rangordning
- avropsform
- tvingande
graph_relations:
- type: CONDITIONAL_ON
  target: volume_hours
constraints:
- param: volume_hours
  operator: GT
  value: 320
  unit: hours
  action: TRIGGER_STRATEGY_FKU
  error_msg: Volym över 320 timmar kräver Förnyad Konkurrensutsättning.
---

# Regel: Avropsform baserat på volym (320-timmarsregeln)
**OM** uppdragets volym är 320 timmar eller mindre:
**DÅ** SKA avrop ske via Dynamisk Rangordning.

**OM** uppdragets volym är MER ÄN 320 timmar:
**DÅ** MÅSTE avrop ske via Förnyad Konkurrensutsättning (FKU).