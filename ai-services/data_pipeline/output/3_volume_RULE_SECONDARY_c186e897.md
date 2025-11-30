---
uuid: c186e897-40c2-41ce-b3ad-5fc62a7108d1
doc_type: smart_block
source_file: 1-AllDocuments (31).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Optionsrätt
- Kontraktsförlängning
entities:
- Inera AB
tags:
- avtalstid
- option
- förlängning
- kontrakt
- villkor
constraints:
- param: contract_length_months
  operator: MAX
  value: 36
  unit: months
  action: BLOCK
  error_msg: Total avtalstid, inklusive optioner, får ej överstiga 36 månader för
    detta avrop.
---

# Regel: Kontraktstid i Avrop
Avropskontraktet löper initialt i tolv (12) månader. Beställaren (Inera) har en ensidig optionsrätt att förlänga kontraktet med upp till tjugofyra (24) ytterligare månader. Total maximal kontraktstid är 36 månader. Meddelande om förlängning ska ske senast fyra (4) veckor innan avtalet löper ut.