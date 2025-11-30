---
uuid: 69a8844b-e865-4d41-81e1-86abed779d74
doc_type: smart_block
source_file: 1-AllDocuments (12).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
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
- avtalstid
- kontraktstid
- option
- förlängning
- år_2023
constraints:
- param: contract_extension_months
  operator: MAX
  value: 12
  unit: months
  action: BLOCK
  error_msg: Maximal förlängningstid är 12 månader.
---

# Regel: Kontraktstid för Inera SDK-projekt
Avropskontraktet gäller initialt till 2023-12-31. Inera har en ensidig optionsrätt att förlänga avtalet vid ett eller flera tillfällen, upp till maximalt totalt tolv (12) månader. Förlängning måste meddelas senast två veckor innan avtalet löper ut.