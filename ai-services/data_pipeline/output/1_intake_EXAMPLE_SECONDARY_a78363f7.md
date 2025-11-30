---
uuid: a78363f7-225d-4f44-9bb5-4ec16c6fd0da
doc_type: smart_block
source_file: 1-AllDocuments (32).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Kompetenskrav
- Erfarenhetskrav
- Teknisk kompetens
- Ska-krav
entities:
- Senior infrastrukturarkitekt
- Nivå 5
- kubernetes
- Hybridlösningar
tags:
- exempel
- ska_krav
- kompetenskrav
- nivå_5
- senior_infrastrukturarkitekt
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Konsulten måste uppfylla kraven för Nivå 5.
- param: experience_it_architecture_years
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av IT-arkitektur inom infrastruktur.
- param: experience_hybrid_solutions_years
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av hybridlösningar.
- param: experience_container_solutions_years
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av containerlösningar (kubernetes).
---

# Exempel: Ska-krav för Senior Infrastrukturarkitekt (Nivå 5)
Ett exempel på obligatoriska kompetenskrav (ska-krav) för en konsult på Nivå 5, utöver ramavtalets generella krav.

- **Nivå:** 5
- **Erfarenhet IT-arkitektur/infrastruktur:** Minst 5 år
- **Erfarenhet Hybridlösningar (Onprem, IaaS, PaaS, SaaS):** Minst 2 år
- **Erfarenhet Containerlösningar (kubernetes) & Mikrotjänster:** Minst 5 år
- **Uppdrag inom säkerhetslösningar:** Minst 2
- **Uppdrag med ansvar för moderna plattformar:** Minst 2
- **Uppdrag med framtagande av nulägesanalys:** Minst 2
- **Uppdrag med framtagande av transformationskarta:** Minst 1
- **Projekterfarenhet från offentlig sektor:** Minst 1