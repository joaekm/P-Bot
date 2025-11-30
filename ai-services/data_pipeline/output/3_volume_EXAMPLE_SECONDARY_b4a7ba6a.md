---
uuid: b4a7ba6a-34dc-49b3-8116-d20874db6c44
doc_type: smart_block
source_file: 1-AllDocuments (20).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_3_volume
topic_tags:
- Kontraktstid
- Avtalstid
- Option
- Förlängning
entities:
- Inera AB
tags:
- exempel
- avtalstid
- option
- år_2024
- mars_31
constraints:
- param: contract_option_months
  operator: MAX
  value: 9
  unit: months
  action: WARN
  error_msg: Den totala optionstiden för detta avrop får ej överstiga 9 månader.
---

# Exempel: Kontraktstid med Option (Inera)
Avropskontraktet löper initialt till 2024-03-31. Därefter har beställaren (Inera) en ensidig optionsrätt att förlänga avtalet vid ett eller flera tillfällen, upp till maximalt nio (9) månader totalt.