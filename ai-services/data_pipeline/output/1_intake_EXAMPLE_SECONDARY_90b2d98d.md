---
uuid: 90b2d98d-4db2-47ea-8306-fc0360763e5e
doc_type: smart_block
source_file: 1-AllDocuments (11).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ARTIFACTS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
topic_tags:
- Referenskrav
- Beviskrav
- Kvalificering
entities:
- Bilaga 1
- NTJP
tags:
- referens
- kvalificering
- bevis
- exempel
constraints:
- param: reference_count
  operator: EQUALS
  value: 2
  unit: null
  action: BLOCK
  error_msg: Exakt två referensuppdrag måste lämnas.
- param: reference_age_years
  operator: MAX
  value: 3
  unit: years
  action: BLOCK
  error_msg: Referensuppdrag får inte vara äldre än 3 år.
---

# Exempel: Krav på Referensuppdrag
Konsulten måste kunna uppvisa två (2) relevanta referensuppdrag. Uppdragen får inte vara äldre än tre (3) år från sista anbudsdag och måste uppfylla specifika kriterier, såsom att ha varit ansvarig integrationsarkitekt för anslutning mot NTJP.