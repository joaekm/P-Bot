---
uuid: 5a86929d-cff2-4969-be40-164c8d083dc4
doc_type: smart_block
source_file: 1-AllDocuments (20).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Rollspecifikation
- Kompetensnivå
- Kravverifiering
entities:
- Verksamhetsarkitekt
- Nivå 5
- Inera AB
- IT-konsulttjänster 2021
tags:
- exempel
- inera
- verksamhetsarkitekt
- nivå_5
- ska_krav
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult måste uppfylla kraven för Nivå 5.
- param: role
  operator: EQUALS
  value: Verksamhetsarkitekt
  unit: null
  action: BLOCK
  error_msg: Rollen för detta avrop är Verksamhetsarkitekt.
---

# Exempel: Krav på Roll och Nivå (Inera)
Detta avrop avser rollen **Verksamhetsarkitekt** på **Nivå 5** enligt Addas ramavtal. Anbudsgivaren måste bifoga dokumentation som bevisar att den offererade konsulten uppfyller kraven för Nivå 5.