---
uuid: da44eb13-32cf-4a93-a5d3-bddd160ad687
doc_type: smart_block
source_file: 1-AllDocuments (32).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Optionsrätt
- Förlängning
- Avtalsvillkor
entities:
- Inera AB
tags:
- avtalstid
- option
- förlängning
- år_2024
- september_30
constraints:
- param: contract_extension_months
  operator: MAX
  value: 3
  unit: months
  action: BLOCK
  error_msg: Total förlängning får ej överstiga 3 månader.
- param: extension_notice_weeks
  operator: MIN
  value: 2
  unit: weeks
  action: WARN
  error_msg: Beställaren ska meddela förlängning senast 2 veckor innan avtalsslut.
---

# Regel: Avtalstid och Optionsrätt (Inera-exempel)
Avropskontraktet löper initialt till ett fast slutdatum (2024-09-30) med en ensidig optionsrätt för beställaren (Inera) att förlänga.

- **Maximal förlängning:** Upp till tre (3) månader, kan nyttjas vid ett eller flera tillfällen.
- **Avisering:** Förlängning ska meddelas senast två (2) veckor innan avtalet löper ut.