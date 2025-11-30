---
uuid: 5289eb7e-55d6-4670-8f1b-83473fdb3c0f
doc_type: smart_block
source_file: 1-AllDocuments (25).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Rollbeskrivning
- Kompetenskrav
- Erfarenhetskrav
- Systemintegration
- API-utveckling
entities:
- Integrationsarkitekt
- Nivå 5
- REST-API
- Python
- Docker
tags:
- integrationsarkitekt
- nivå_5
- ska_krav
- erfarenhetskrav
- rest_api
- python
- docker
constraints:
- param: experience_integration_architecture_years
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Konsulten måste ha minst 5 års erfarenhet av integrationsarkitektur.
- param: experience_rest_api_years
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Konsulten måste ha minst 3 års erfarenhet av REST-API:er.
- param: experience_system_integration_apps_years
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Konsulten måste ha minst 3 års erfarenhet av applikationsutveckling inom
    systemintegration.
---

# Definition: Kompetensprofil Integrationsarkitekt (Nivå 5)
Enligt avropsförfrågan från Inera ska en offererad konsult för rollen Integrationsarkitekt (Nivå 5) uppfylla följande obligatoriska krav (ska-krav):

*   **Integrationsarkitektur:** Minst fem (5) års erfarenhet.
*   **REST-API:** Minst tre (3) års erfarenhet av att utforma och bygga.
*   **Systemintegration:** Minst tre (3) års erfarenhet av att skriva applikationer inom området.
*   **Teknik:** Erfarenhet av Python och Docker.
*   **Dokumentation:** Måste ha haft minst tre (3) uppdrag som inkluderat att skriva teknisk dokumentation.