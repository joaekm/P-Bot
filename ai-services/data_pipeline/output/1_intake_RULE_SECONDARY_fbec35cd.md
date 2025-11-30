---
uuid: fbec35cd-bdec-485c-8ba5-e3421bc486c0
doc_type: smart_block
source_file: 1-AllDocuments (8).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
topic_tags:
- Placeringsort
- Säkerhetskrav
- Språkkrav
- Geografi
entities:
- Stockholm
- EU/EES
tags:
- geografi
- stockholm
- säkerhet
- språk
constraints:
- param: location
  operator: ONE_OF
  value:
  - Stockholm
  action: BLOCK
  error_msg: Uppdraget kräver möjlighet till arbete på plats i Stockholm.
- param: consultant_residency
  operator: ONE_OF
  value:
  - EU
  - EES
  action: BLOCK
  error_msg: Konsulten måste vara placerad inom EU/EES.
---

# Regel: Placeringsort och Säkerhetskrav
Uppdraget ska kunna utföras på plats i Stockholm. Av säkerhetsskäl måste konsulten vara placerad inom EU/EES. Konsulten måste kunna uttrycka sig på svenska i tal och skrift.