---
uuid: 7be66c6c-6b1d-4637-a573-63fef97a682c
doc_type: smart_block
source_file: 1-AllDocuments (30).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_2_level
topic_tags:
- Kompetensnivå
- Kravuppfyllnad
- Obligatoriskt krav
entities:
- Nivå 5
tags:
- nivå_5
- kompetenskrav
- ska_krav
- expert
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult måste uppfylla kraven för Nivå 5.
---

# Regel: Krav på Kompetensnivå 5
I Ineras avrop för IT-driftsutredning ställs ett ovillkorligt krav på att båda offererade konsulter (Senior IT arkitekt infrastruktur och Senior Nätverksarkitekt) måste uppfylla kraven för **Nivå 5** enligt ramavtalet.