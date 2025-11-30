---
uuid: 5868c2bb-76e6-4721-bd68-2b6cb3b5aa1e
doc_type: smart_block
source_file: 1-AllDocuments (25).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Placeringsort
- Geografiskt krav
- Språkkrav
entities:
- Stockholm
- EU/EES
tags:
- stockholm
- eu_ees
- svenska
- språkkrav
- geografi
constraints:
- param: location_work
  operator: EQUALS
  value: Stockholm
  action: BLOCK
  error_msg: Uppdraget kräver närvaro på plats i Stockholm.
- param: location_consultant_residency
  operator: ONE_OF
  value:
  - EU
  - EES
  action: BLOCK
  error_msg: Konsulten måste vara placerad inom EU/EES.
- param: language_swedish
  operator: EQUALS
  value: true
  action: BLOCK
  error_msg: Svenska i tal och skrift är ett krav.
---

# Regel: Geografiska Krav och Språkkrav
För detta uppdrag gäller följande krav:

*   **Ort för utförande:** Uppdraget ska kunna utföras på plats i Stockholm.
*   **Placering av konsult:** Konsulten måste vara placerad inom EU/EES av säkerhetsskäl.
*   **Språk:** Konsulten måste kunna uttrycka sig obehindrat på svenska i tal och skrift.