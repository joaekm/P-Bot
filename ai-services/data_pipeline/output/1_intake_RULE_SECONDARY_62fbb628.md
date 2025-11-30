---
uuid: 62fbb628-a8d6-4545-b14c-9649f1426feb
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ARTIFACTS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Referenskrav
- Kvalificering
- Beviskrav
entities:
- Bilaga 1
tags:
- referens
- kvalificering
- bilaga
constraints:
- param: reference_count
  operator: EQUALS
  value: 3
  action: BLOCK
  error_msg: Exakt tre referensuppdrag ska inkomma.
- param: reference_max_age_years
  operator: MAX
  value: 3
  unit: years
  action: BLOCK
  error_msg: Referensuppdrag får inte vara äldre än 3 år från sista anbudsdag.
---

# Regel: Krav på Referensuppdrag
Anbudsgivaren SKA inkomma med tre (3) referensuppdrag för den offererade konsulten. Referenserna får inte vara äldre än tre (3) år från sista anbudsdag och ska styrka specifik erfarenhet enligt bilaga 1.