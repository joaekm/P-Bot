---
uuid: ff4f0aa1-48ed-4a52-9719-78eddcd25c3c
doc_type: smart_block
source_file: 1-AllDocuments (17).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Rollkrav
- Kompetensnivå
- Beviskrav
- Kvalificering
entities:
- Nivå 5
tags:
- rollkrav
- kompetensnivå
- nivå_5
- bevis
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult måste uppfylla kraven för Nivå 5.
---

# Regel: Krav på kompetensnivå och bevis
Offererad konsult ska vara på nivå 5 enligt ramavtalet. Dokumentation som bevisar att konsulten uppfyller kraven för nivå 5 måste bifogas anbudet.