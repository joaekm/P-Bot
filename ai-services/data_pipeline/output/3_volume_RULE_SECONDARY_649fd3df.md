---
uuid: 649fd3df-ec10-43b9-b8ba-936eb0b62534
doc_type: smart_block
source_file: 1-AllDocuments (28).pdf
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
- Kontraktsvillkor
entities:
- Inera AB
- Avropskontrakt
tags:
- avtalstid
- option
- förlängning
- kontrakt
- 12_månader
- 24_månader
- maximal_avtalstid
constraints:
- param: total_contract_length_months
  operator: MAX
  value: 36
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive optioner får ej överstiga 36 månader.
---

# Regel: Kontraktstid och Förlängningsoption (Exempel Inera)
I detta specifika avrop gäller följande avtalstider:

- **Initial avtalstid:** 12 månader.
- **Förlängningsoption:** Inera har en ensidig rätt att förlänga avtalet med upp till maximalt 24 månader.
- **Total max-tid:** 36 månader (12 + 24).
- **Avisering:** Förlängning ska meddelas senast fyra (4) veckor innan avtalet löper ut.