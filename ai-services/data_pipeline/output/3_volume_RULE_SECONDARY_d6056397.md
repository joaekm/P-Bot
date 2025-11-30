---
uuid: d6056397-5c95-4b02-b8d7-7b46d4648453
doc_type: smart_block
source_file: 1-AllDocuments (24).pdf
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
- Volym
- Budget
entities: []
tags:
- takpris
- timpris
- budget
- ekonomi
constraints:
- param: hourly_rate
  operator: MAX
  value: 1350
  unit: sek
  action: BLOCK
  error_msg: Timpriset får ej överstiga 1350 SEK.
---

# Regel: Finansiella villkor för avrop
Specifika finansiella ramar gäller för detta avrop.

- **Takpris:** Det fasta timpriset får inte överstiga 1350 SEK, exklusive moms.
- **Uppskattat värde:** Avropets uppskattade värde per avtalsår är 600 000 SEK. Inga volymer garanteras.