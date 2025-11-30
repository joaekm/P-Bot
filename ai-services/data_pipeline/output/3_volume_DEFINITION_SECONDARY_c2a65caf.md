---
uuid: c2a65caf-5c30-4f04-adc4-ab3dfafe5ec9
doc_type: smart_block
source_file: 1-AllDocuments (22).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Kontraktstid
- Option
- Förlängning
entities: []
tags:
- avtalstid
- option
- år_2024
- januari_01
- oktober_31
constraints:
- param: contract_length_months
  operator: MAX
  value: 34
  unit: months
  action: WARN
  error_msg: Total avtalstid inklusive maximal option är 34 månader.
---

# Definition: Kontraktstid och Option
Avropskontraktet löper initialt från 2024-01-01 till 2024-10-31 (10 månader). Inera har en ensidig optionsrätt att förlänga avtalet med upp till tjugofyra (24) månader, vid ett eller flera tillfällen.