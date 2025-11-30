---
uuid: 15de2f66-3e4d-43dc-bfbc-cd1329c69c9d
doc_type: smart_block
source_file: 1-AllDocuments (8).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ARTIFACTS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
topic_tags:
- Referenskrav
- Anbudsvillkor
- Kvalificering
entities: []
tags:
- referens
- cv
- kvalificering
constraints:
- param: reference_project_age_years
  operator: MAX
  value: 3
  unit: years
  action: BLOCK
  error_msg: Referensuppdrag får inte vara äldre än 3 år.
- param: reference_project_count
  operator: EQUALS
  value: 2
  action: BLOCK
  error_msg: Två referensuppdrag måste anges per konsult.
---

# Regel: Krav på Referensuppdrag
Anbudsgivaren ska redovisa två referensuppdrag per konsult. Uppdragen får inte vara äldre än tre (3) år. Minst ett av referensuppdragen måste vara avslutat.