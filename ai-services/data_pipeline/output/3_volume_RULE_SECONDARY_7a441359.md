---
uuid: 7a441359-03f0-4ea5-91b1-44d86198c05c
doc_type: smart_block
source_file: 1-AllDocuments (25).pdf
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
- Kontraktsvärde
entities:
- Inera AB
- IT-konsulttjänster 2021
tags:
- avtalstid
- kontraktsvärde
- option
- förlängning
constraints:
- param: contract_total_length_months
  operator: MAX
  value: 12
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive option får ej överstiga 12 månader.
---

# Regel: Kontraktstid och Omfattning (Inera-avrop)
Avropskontraktet för detta uppdrag har en initial löptid på sex (6) månader. Beställaren (Inera) har en ensidig optionsrätt att förlänga avtalet med upp till ytterligare sex (6) månader. Maximal total kontraktstid är tolv (12) månader. Det uppskattade kontraktsvärdet är 1 700 000 SEK, men inga volymer garanteras.