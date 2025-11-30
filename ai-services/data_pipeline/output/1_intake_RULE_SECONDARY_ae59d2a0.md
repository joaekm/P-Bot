---
uuid: ae59d2a0-afce-454f-b2c8-6a78a4e41e64
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Kompetensnivå
- Rollkrav
- Kvalificering
entities:
- Senior Fullstackutvecklare
- Nivå 5
tags:
- rollkrav
- nivå_5
- senior
- kvalificering
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult måste uppfylla Nivå 5 enligt ramavtalet.
- param: role_title
  operator: EQUALS
  value: Senior Fullstackutvecklare
  action: BLOCK
  error_msg: Rollen som efterfrågas är Senior Fullstackutvecklare.
---

# Regel: Krav på Roll och Nivå
Avropet avser en (1) konsult för rollen Senior Fullstackutvecklare. Konsulten SKA uppfylla kraven för Nivå 5 enligt ramavtalet. Bevis för nivåuppfyllnad måste bifogas anbudet.