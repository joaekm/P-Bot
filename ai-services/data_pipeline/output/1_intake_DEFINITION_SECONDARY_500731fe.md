---
uuid: 500731fe-83a2-49a9-8aad-1016192ee414
doc_type: smart_block
source_file: 1-AllDocuments (30).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Erfarenhetskrav
- Kompetenskrav
- Rollbeskrivning
- IT-arkitektur
entities:
- Senior IT-arkitekt infrastruktur
- Kubernetes
- Hybridlösningar
- Offentlig sektor
tags:
- ska_krav
- erfarenhet
- cv_krav
- it_arkitekt
- infrastruktur
constraints:
- param: experience_years_it_architecture
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av IT-arkitektur/infrastruktur.
- param: experience_years_hybrid_solutions
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av hybridlösningar.
- param: experience_years_container_solutions
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av containerlösningar.
---

# Definition: Exempel på erfarenhetskrav (Senior IT-arkitekt)
Ett exempel på specifika erfarenhetskrav ("ska-krav") från ett avrop. För rollen Senior IT-arkitekt Infrastruktur krävdes bland annat:

*   Minst 5 års erfarenhet av IT-arkitektur inom infrastruktur/IT-drift.
*   Minst 2 års arbete med hybridlösningar (On-prem, IaaS, PaaS, SaaS).
*   Minst 5 års erfarenhet av containerlösningar (kubernetes) och microtjänster.
*   Minst 1 uppdrag inom offentlig sektor relaterat till IT-drift.