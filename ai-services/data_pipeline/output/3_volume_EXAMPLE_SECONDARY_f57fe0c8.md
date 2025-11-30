---
uuid: f57fe0c8-390b-453e-bf48-c3d7b0bf3426
doc_type: smart_block
source_file: 1-AllDocuments (17).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Option
- Förlängning
entities:
- Avropskontrakt
tags:
- avtalstid
- option
- kontraktstid
- förlängning
constraints:
- param: contract_length_months
  operator: MAX
  value: 36
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive optioner får ej överstiga 36 månader.
---

# Exempel: Kontraktstid med option
Ett avropskontrakt kan struktureras med en initial period och en ensidig optionsrätt för beställaren att förlänga. I detta fall är den initiala tiden ett (1) år med option på förlängning upp till maximalt tjugofyra (24) ytterligare månader. Total möjlig avtalstid är 36 månader.