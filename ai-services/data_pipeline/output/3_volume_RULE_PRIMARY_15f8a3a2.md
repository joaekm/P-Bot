---
uuid: 15f8a3a2-efb5-4ab5-8191-ace0c7165fc9
doc_type: smart_block
source_file: kontraktsvillkor-dynamisk-rangordning---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Betalningsvillkor
- Fakturering
- Förfallodag
entities: []
tags:
- betalningsvillkor
- 30_dagar
- faktura
constraints:
- param: payment_term
  operator: MAX
  value: 30
  unit: days
  action: BLOCK
  error_msg: Betalningsvillkor får ej överstiga 30 dagar.
---

# Regel: Betalningsvillkor för faktura
En korrekt och fullständig faktura SKA betalas senast 30 kalenderdagar efter att leverantören skickat den.