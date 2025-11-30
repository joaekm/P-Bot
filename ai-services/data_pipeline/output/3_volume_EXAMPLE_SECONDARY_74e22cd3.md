---
uuid: 74e22cd3-9c9d-46f6-9f30-372c7231fa76
doc_type: smart_block
source_file: 1-AllDocuments (11).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: DOMAIN_KNOWLEDGE
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
- år_2023
- exempel
constraints:
- param: contract_extension_months
  operator: MAX
  value: 6
  unit: months
  action: BLOCK
  error_msg: Maximal förlängningstid är 6 månader.
---

# Exempel: Avtalstid och Förlängning
Avropskontraktet löper initialt till ett specifikt slutdatum (2023-12-31 i exemplet) med en ensidig optionsrätt för kunden att förlänga med upp till sex (6) månader. Meddelande om förlängning ska lämnas senast två veckor innan avtalet löper ut.