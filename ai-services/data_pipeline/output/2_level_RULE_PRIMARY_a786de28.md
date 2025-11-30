---
uuid: a786de28-7f51-4a59-b24c-6c10923849c0
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
- Rollhantering
- Kompetensnivå
entities:
- Dynamisk Rangordning
- 320-timmarsregeln
- Bilaga A
tags:
- dynamisk_rangordning
- dr
- avropsstrategi
- villkor
constraints:
- param: volume_hours
  operator: MAX
  value: 320
  unit: hours
  action: BLOCK
  error_msg: Dynamisk Rangordning kan ej användas för volymer över 320 timmar. Välj
    FKU.
- param: competence_level
  operator: ONE_OF
  value:
  - 1
  - 2
  - 3
  - 4
  unit: level
  action: BLOCK
  error_msg: Dynamisk Rangordning kan ej användas för Nivå 5. Välj FKU.
---

# Regel: Villkor för Dynamisk Rangordning
Dynamisk Rangordning får **ENDAST** användas om **ALLA** följande villkor är uppfyllda:
1.  Uppdragets totala volym är **maximalt 320 timmar** (inklusive optioner).
2.  En av de fördefinierade **exempelrollerna** från Bilaga A används.
3.  Kompetensnivå **1, 2, 3 eller 4** efterfrågas.