---
uuid: f07b2415-5305-4c6e-a461-4f87a1879cb7
doc_type: smart_block
source_file: allmanna-kontraktsvillkor-fornyad-konkurrensutsattning---it-konsulttjanster-2021-2025-11-21.docx
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Prissättning
- Takpris
- FKU
entities:
- IT-konsulttjänster 2021
tags:
- takpris
- pris
- fku
constraints:
- param: hourly_rate
  operator: MAX
  value: FROM_FRAMEWORK_AGREEMENT
  unit: sek
  action: BLOCK
  error_msg: Timpriset får inte överstiga gällande takpris i ramavtalet.
---

# Regel: Pristak vid Förnyad Konkurrensutsättning
De priser som offereras i en förnyad konkurrensutsättning FÅR ALDRIG överstiga de gällande takpriserna i ramavtalet.