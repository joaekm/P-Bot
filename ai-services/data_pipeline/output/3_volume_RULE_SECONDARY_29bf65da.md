---
uuid: 29bf65da-6b7d-4b60-a51b-b48a3d73c9fb
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
- Takpris
- Timpris
- Prissättning
- Kostnader
entities:
- Senior systemutvecklare
tags:
- takpris
- timpris
- pris
- sek
- exkl_moms
- all_inclusive
constraints:
- param: hourly_rate
  operator: MAX
  value: 1250
  unit: sek
  action: BLOCK
  error_msg: Timpriset får inte överstiga takpriset på 1250 SEK.
---

# Regel: Takpris för Timarvode (Exempel Inera)
I avropet för Senior Systemutvecklare har ett absolut takpris för timarvodet fastställts.

- **Takpris per timme:** 1250 SEK (exklusive moms).
- **Villkor:** Timpriset måste inkludera samtliga kringkostnader. Ingen separat ersättning utgår för resor, traktamente, logi, etc.