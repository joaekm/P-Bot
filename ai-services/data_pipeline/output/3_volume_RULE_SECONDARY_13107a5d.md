---
uuid: 13107a5d-c2a7-48a0-ba59-fac4fd5a6d93
doc_type: smart_block
source_file: 1-AllDocuments (29).pdf
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
- Förlängning
- Avtalsvillkor
entities:
- '2024-12-31'
- Inera AB
tags:
- avtalstid
- kontraktstid
- option
- förlängning
- år_2024
- december_31
constraints:
- param: contract_extension_months
  operator: MAX
  value: 6
  unit: months
  action: BLOCK
  error_msg: Total förlängning får ej överstiga 6 månader.
---

# Regel: Kontraktstid och Förlängning
Avropskontraktet gäller initialt till och med **2024-12-31**. Inera har en ensidig optionsrätt att förlänga avtalet vid ett eller flera tillfällen, upp till **maximalt sex (6) månader** totalt. Meddelande om förlängning ska ske senast fyra veckor innan avtalet löper ut.