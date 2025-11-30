---
uuid: de533d14-21c9-49ca-a6cb-de32d1365887
doc_type: smart_block
source_file: 1-AllDocuments (15).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Kontraktslängd
- Optionsrätt
entities:
- Inera
tags:
- avtalstid
- option
- förlängning
constraints:
- param: contract_length_months_initial
  operator: EQUALS
  value: 6
  unit: months
  action: BLOCK
  error_msg: Initial avtalstid är 6 månader.
- param: contract_length_months_total
  operator: MAX
  value: 12
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive option får ej överstiga 12 månader.
---

# Regel: Kontraktstid och Option
Avropskontraktet gäller initialt i sex (6) månader. Därefter har beställaren (Inera) en ensidig rätt att förlänga avtalet med upp till ytterligare sex (6) månader. Maximal total kontraktstid är tolv (12) månader.