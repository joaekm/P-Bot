---
uuid: effb573d-9197-4321-8ff7-e800e1602dc9
doc_type: smart_block
source_file: Upphandlingsdokument (GDPR).pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalsperiod
- Maximal avtalstid
- Giltighetstid
entities:
- IT-konsulttjänster 2021
tags:
- avtalstid
- ramavtal
- 4_år
- kontraktsvillkor
constraints:
- param: contract_length_months
  operator: MAX
  value: 48
  unit: months
  action: BLOCK
  error_msg: Ramavtalstiden får ej överstiga 48 månader (4 år).
---

# Regel: Maximal Ramavtalsperiod
Ramavtalets totala längd FÅR EJ överstiga fyra (4) år (48 månader). Ramavtalet löper ut automatiskt efter denna period utan föregående uppsägning.