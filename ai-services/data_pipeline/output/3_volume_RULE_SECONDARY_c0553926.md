---
uuid: c0553926-04a1-4707-a872-345ad1acf165
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Option
- Förlängning
entities:
- Inera AB
tags:
- avtalstid
- kontrakt
- option
- förlängning
constraints:
- param: contract_length_months
  operator: MAX
  value: 36
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive optioner får ej överstiga 36 månader (12 +
    24).
---

# Regel: Maximal Kontraktstid
Avropskontraktet löper initialt ett (1) år. Beställaren (Inera) har en ensidig optionsrätt att förlänga avtalet vid ett eller flera tillfällen.

- **Initial period:** 12 månader
- **Maximal total förlängning:** 24 månader
- **Maximal total kontraktstid:** 36 månader