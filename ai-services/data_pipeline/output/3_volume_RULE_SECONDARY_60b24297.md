---
uuid: 60b24297-3b6a-442a-926c-f640c503823f
doc_type: smart_block
source_file: 1-AllDocuments (22).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Takpris
- Timpris
- Prisbegränsning
entities:
- Senior Mjukvaruarkitekt
- Senior Infrastrukturarkitekt
- Senior Utvecklare
- Senior Lösningsarkitekt
tags:
- takpris
- timpris
- kostnad
- regel
constraints:
- param: hourly_rate
  operator: MAX
  value: 1450
  unit: sek
  action: BLOCK
  error_msg: Timpriset för Senior Infrastrukturarkitekt får ej överstiga 1450 SEK.
  context:
    role: Senior Infrastrukturarkitekt
- param: hourly_rate
  operator: MAX
  value: 1300
  unit: sek
  action: BLOCK
  error_msg: Timpriset för rollen får ej överstiga 1300 SEK.
  context:
    role:
    - Senior Mjukvaruarkitekt
    - Senior Lösningsarkitekt
- param: hourly_rate
  operator: MAX
  value: 1250
  unit: sek
  action: BLOCK
  error_msg: Timpriset för Senior Utvecklare får ej överstiga 1250 SEK.
  context:
    role: Senior Utvecklare
---

# Regel: Takpriser per roll
Följande maximala timpriser (takpriser) exklusive moms gäller för respektive roll:
- **Senior Mjukvaruarkitekt:** 1300 SEK
- **Senior Infrastrukturarkitekt:** 1450 SEK
- **Senior Utvecklare:** 1250 SEK
- **Senior Lösningsarkitekt:** 1300 SEK