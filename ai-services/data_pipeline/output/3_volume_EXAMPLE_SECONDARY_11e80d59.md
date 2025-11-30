---
uuid: 11e80d59-1598-4c4e-9887-b95e7572c669
doc_type: smart_block
source_file: 1-AllDocuments (9).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Kontraktsförlängning
- Optionsrätt
entities: []
tags:
- exempel
- avtalstid
- option
- förlängning
constraints:
- param: contract_extension_months
  operator: MAX
  value: 12
  unit: months
  action: BLOCK
  error_msg: Maximal förlängningstid är 12 månader.
---

# Exempel: Kontraktstid med Option
Avropskontraktet gällde initialt till ett fast slutdatum (2023-12-31) med en ensidig optionsrätt för beställaren (Inera) att förlänga avtalet upp till maximalt tolv (12) månader.