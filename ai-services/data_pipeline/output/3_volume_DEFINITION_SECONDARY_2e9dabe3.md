---
uuid: 2e9dabe3-39c1-4ad2-886b-71a9b746f9b3
doc_type: smart_block
source_file: 1-AllDocuments (30).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Option
- Förlängning
- Kontraktsvillkor
entities: []
tags:
- avtalstid
- option
- kontraktstid
- förlängning
constraints:
- param: contract_extension_months
  operator: MAX
  value: 2
  unit: months
  action: WARN
  error_msg: Total förlängning via option får ej överstiga 2 månader.
---

# Definition: Exempel på Avtalstid och Option
Avropskontraktet löper initialt till ett fast slutdatum (2024-09-30) med en ensidig optionsrätt för beställaren (Inera) att förlänga avtalet vid ett eller flera tillfällen, upp till maximalt två (2) månader totalt. Meddelande om förlängning ska ske senast två veckor innan avtalet löper ut.