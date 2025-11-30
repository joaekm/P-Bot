---
uuid: 5b691356-c6e6-4d9c-9f3d-253a1c08473c
doc_type: smart_block
source_file: 1-AllDocuments (15).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
topic_tags:
- Placeringsort
- Geografiskt krav
- Språkkrav
- Säkerhetskrav
entities:
- Stockholm
- EU/EES
tags:
- geografi
- språk
- säkerhet
- stockholm
- eu_ees
constraints:
- param: location
  operator: ONE_OF
  value:
  - EU
  - EES
  action: BLOCK
  error_msg: Konsulten måste vara placerad inom EU/EES.
- param: language
  operator: EQUALS
  value: Swedish
  action: BLOCK
  error_msg: Konsulten måste behärska svenska i tal och skrift.
---

# Regel: Arbetsplats och Språkkrav
Uppdraget ska kunna utföras på plats i Stockholm. Konsulten MÅSTE vara fysiskt placerad inom EU/EES av säkerhetsskäl. Verksamhetskravet är att konsulten kan uttrycka sig obehindrat på svenska i både tal och skrift.