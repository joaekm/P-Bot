---
uuid: 7f5b32d0-6b1d-43bf-9cb0-16312aced5fe
doc_type: smart_block
source_file: 1-AllDocuments (6).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Förlängning
- Optionsrätt
- Kontraktsvillkor
entities:
- Avropskontrakt
tags:
- exempel
- avtalstid
- option
- år_2023
- kontrakt
constraints:
- param: contract_extension_months
  operator: MAX
  value: 6
  unit: months
  action: BLOCK
  error_msg: Förlängningsoptionen får ej överstiga 6 månader.
---

# Exempel: Avtalstid med Option
Ett avropskontrakt kan ha en fast initial tid och en ensidig optionsrätt för kunden att förlänga.

**Exempel (Inera Processledare):**
- **Initial tid:** Kontraktstecknande till 2023-12-31.
- **Option:** Kunden (Inera) har rätt att förlänga avtalet med upp till maximalt sex (6) månader.
- **Avisering:** Förlängning måste meddelas senast fyra veckor innan avtalet löper ut.