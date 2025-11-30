---
uuid: f77b77ac-ce3a-4a53-b886-fba44af1fa19
doc_type: smart_block
source_file: 1-AllDocuments (24).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Förlängningsoption
- Kontraktsvillkor
entities: []
tags:
- avtalstid
- option
- kontrakt
- år_2024
- januari_01
- oktober_31
constraints:
- param: contract_length_months
  operator: MAX
  value: 34
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive optioner får ej överstiga 34 månader.
---

# Definition: Avtalstid och förlängning
- **Initial avtalstid:** Gäller från 2024-01-01 till och med 2024-10-31 (10 månader).
- **Option:** Beställaren (Inera) har en ensidig rätt att förlänga avtalet med upp till tjugofyra (24) månader, vid ett eller flera tillfällen.
- **Total maximal avtalstid:** 34 månader (10 + 24).
- **Avisering:** Förlängning måste meddelas senast fyra (4) veckor innan avtalet löper ut.