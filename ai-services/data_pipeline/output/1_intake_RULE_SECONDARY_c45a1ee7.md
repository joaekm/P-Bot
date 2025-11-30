---
uuid: c45a1ee7-de67-40c0-8b2d-46e1187c0e20
doc_type: smart_block
source_file: 1-AllDocuments (21).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Geografiska krav
- Språkkrav
- Säkerhetskrav
- Placeringsort
entities:
- EU/EES
- Stockholm
tags:
- geografi
- språk
- krav
- säkerhet
- stockholm
- eu_ees
constraints:
- param: location
  operator: ONE_OF
  value:
  - EU/EES
  action: BLOCK
  error_msg: Konsult måste vara placerad inom EU/EES av säkerhetsskäl.
- param: language_swedish
  operator: EQUALS
  value: true
  action: BLOCK
  error_msg: Verksamhetskrav på att kunna uttrycka sig i svenska i både tal och skrift.
---

# Regel: Placerings- och språkkrav
Av säkerhetstekniska och verksamhetsmässiga skäl kan krav ställas på konsultens placering och språkfärdigheter.

**Exempel från Inera-avrop:**
- **Placering:** Konsulten måste vara placerad inom EU/EES.
- **Arbetsplats:** Uppdraget ska med kort varsel kunna utföras på plats i Stockholm.
- **Språk:** Konsulten måste kunna uttrycka sig på svenska i både tal och skrift.