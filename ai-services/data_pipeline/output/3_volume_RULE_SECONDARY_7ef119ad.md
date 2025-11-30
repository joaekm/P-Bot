---
uuid: 7ef119ad-df16-4f02-9144-2e214470ebc7
doc_type: smart_block
source_file: 1-AllDocuments (8).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: GENERAL_LEGAL
suggested_phase:
- step_3_volume
topic_tags:
- Prissättning
- Valuta
- Moms
entities:
- SEK
tags:
- pris
- sek
- valuta
- moms
constraints:
- param: currency
  operator: EQUALS
  value: SEK
  action: BLOCK
  error_msg: Alla priser måste anges i SEK.
---

# Regel: Prisangivelse i SEK exkl. moms
Alla priser i anbudet ska anges i svenska kronor (SEK) och vara exklusive mervärdesskatt (moms).