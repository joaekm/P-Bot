---
uuid: a459da8f-9984-4ce6-a1fc-0d2ff900b324
doc_type: smart_block
source_file: 1-AllDocuments (15).pdf
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
- Kravuppfyllnad
- Anbudskrav
entities:
- Nivå 5
- IT och informationssäkerhet
tags:
- nivå_5
- kompetenskrav
- tvingande
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult måste vara på Nivå 5.
---

# Regel: Krav på Kompetensnivå
Den offererade konsulten för rollen inom 'IT och informationssäkerhet' MÅSTE uppfylla kraven för Nivå 5 enligt ramavtalet. Bevis för detta SKA bifogas anbudet.