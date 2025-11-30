---
uuid: 1738462b-aa8e-4bfd-affa-0ac098e266a8
doc_type: smart_block
source_file: 1-AllDocuments (12).pdf
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
- Arbetsfördelning
- Teambud
entities:
- Projektledare
- Nivå 4
- Nivå 3
tags:
- nivå_4
- nivå_3
- projektledare
- krav
- team
- arbetsfördelning
constraints:
- param: primary_consultant_level
  operator: EQUALS
  value: 4
  unit: level
  action: BLOCK
  error_msg: Offererad huvudkonsult/ansvarig projektledare måste vara på Nivå 4.
- param: secondary_consultant_level
  operator: MIN
  value: 3
  unit: level
  action: BLOCK
  error_msg: En eventuell andra konsult i ett team måste vara minst på Nivå 3.
- param: max_consultants
  operator: MAX
  value: 2
  unit: persons
  action: BLOCK
  error_msg: Maximalt två konsulter får offereras för uppdraget.
- param: primary_consultant_workload_percent
  operator: MIN
  value: 70
  unit: percent
  action: BLOCK
  error_msg: Ansvarig projektledare måste utföra minst 70% av uppdraget.
---

# Regel: Krav på roll och nivå (Inera SDK)
För uppdraget som projektledare gäller följande kompetensnivåer:
- **En konsult:** Offererad konsult MÅSTE vara på Nivå 4.
- **Team (max 2 pers):** Om ett team offereras, MÅSTE ansvarig projektledare vara Nivå 4 och den andra konsulten minst Nivå 3.
- **Arbetsfördelning i team:** Ansvarig projektledare (Nivå 4) MÅSTE utföra minst 70% av uppdraget.