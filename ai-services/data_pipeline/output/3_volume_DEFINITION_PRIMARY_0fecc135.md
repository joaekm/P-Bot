---
uuid: 0fecc135-1b89-4d0c-ac75-81fcdcb0dbcd
doc_type: smart_block
source_file: Fr†gor och svar under anbudstiden (GDPR).pdf
authority_level: PRIMARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Ansvarsbegränsning
- Skadestånd
- Avtalsvillkor
- Riskhantering
entities: []
tags:
- ansvarsbegränsning
- skadestånd
- kontraktsvillkor
- maxbelopp
constraints:
- param: liability_cap_sek_per_year
  operator: MAX
  value: 5000000
  unit: sek
  action: BLOCK
  error_msg: Ansvaret för ren förmögenhetsskada är begränsat till 5 MSEK per år.
---

# DEFINITION: Ansvarsbegränsning är ett fast belopp
Ansvarsbegränsningen för ren förmögenhetsskada är ett fast takbelopp på 5 miljoner SEK per skada och per år. Beloppet är inte en procentsats av kontraktets värde och kommer inte att justeras.