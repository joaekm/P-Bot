---
uuid: 2e553ef7-e22d-4981-9490-dfee287d22aa
doc_type: smart_block
source_file: Upphandlingsdokument (GDPR).pdf
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
- Tröskelvärde
entities:
- Dynamisk Rangordning
- 320-timmarsregeln
- Nivå 1-4
tags:
- dynamisk_rangordning
- dr
- 320_timmarsregeln
- volymgräns
- kompetensnivå
constraints:
- param: volume_hours
  operator: MAX
  value: 320
  unit: hours
  action: BLOCK
  error_msg: Dynamisk Rangordning är endast tillåtet för uppdrag upp till 320 timmar.
    Använd FKU för större uppdrag.
- param: competence_level
  operator: MAX
  value: 4
  unit: level
  action: BLOCK
  error_msg: Dynamisk Rangordning är endast tillåtet för nivå 1-4. Använd FKU för
    Nivå 5.
---

# Regel: Villkor för Dynamisk Rangordning
**OM** avropsformen är Dynamisk Rangordning (DR):
**DÅ** MÅSTE följande villkor vara uppfyllda:
1.  **Volym:** Total omfattning FÅR EJ överstiga 320 timmar (inklusive eventuella optioner).
2.  **Kompetens:** Endast kompetensnivå 1, 2, 3, eller 4 får efterfrågas.
3.  **Roller:** Endast de fördefinierade exempelrollerna får användas.