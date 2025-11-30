---
uuid: 772c0dc4-7860-4ca0-b428-18e0eef12546
doc_type: smart_block
source_file: 1-AllDocuments (32).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Timpris
- Takpris
- Kostnadsmodell
- Fakturering
entities:
- Senior infrastrukturarkitekt
tags:
- takpris
- timpris
- fastpris
- inga_tilläggskostnader
constraints:
- param: hourly_rate
  operator: MAX
  value: 1300
  unit: sek
  action: BLOCK
  error_msg: Timpriset får inte överstiga takpriset på 1300 SEK.
---

# Regel: Takpris och Kostnadsmodell (Inera-exempel)
För avropet gäller ett fast takpris per timme. Inga andra kostnader ersätts.

- **Takpris:** 1300 SEK/timme (exkl. moms).
- **Inkluderade kostnader:** Priset ska inkludera alla eventuella kringkostnader såsom resor, traktamente, logi, material etc.
- **Regel:** Inga tilläggskostnader accepteras.