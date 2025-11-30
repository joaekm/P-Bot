---
uuid: 03ddddd1-bad4-4545-ae76-13a56ee2b751
doc_type: smart_block
source_file: 1-AllDocuments (29).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_2_level
topic_tags:
- Erfarenhetskrav
- Teknisk kompetens
- Verktygskännedom
- Kvalificeringskrav
entities:
- MongoDB
- DirX
- GDPR
- Jira
- Confluence
- Excel
- Lucid charts
tags:
- ska_krav
- erfarenhet
- cv_krav
- gdpr
- jira
- mongodb
constraints:
- param: experience_years_database
  operator: MIN
  value: 1
  unit: years
  action: BLOCK
  error_msg: Kräver minst 1 års erfarenhet av databasverktyg.
- param: experience_years_migration_communication
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av kommunikation kring migreringar.
- param: experience_projects_gdpr
  operator: MIN
  value: 1
  unit: projects
  action: BLOCK
  error_msg: Kräver erfarenhet från minst 1 GDPR-relaterat projekt.
- param: experience_years_agile_tools
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av Jira och Confluence.
---

# Regel: Obligatoriska Erfarenhetskrav (Ska-krav)
Offererad konsult måste, via CV, tydligt uppfylla samtliga följande krav:

- **Databasverktyg:** Minst 1 års erfarenhet (ex. MongoDB, DirX).
- **Extern kommunikation:** Minst 2 års erfarenhet av kommunikation/planering av migreringar.
- **Tekniska presentationer:** Ansvarat för framtagande och hållande av tekniska presentationer i minst 2 olika projekt.
- **Komplex migrering:** Aktivt deltagit i teknisk roll i minst 1 projekt med komplex, affärskritisk migrering under drift.
- **GDPR:** Arbetat i minst 1 projekt som omfattat hantering av personuppgifter och GDPR.
- **Agila verktyg:** Minst 2 års erfarenhet av Jira och Confluence.
- **Datahantering:** Minst 2 års erfarenhet av planering och administration i Excel.
- **Ritverktyg:** Minst 1 års erfarenhet av verktyg för systemsamband (ex. Lucid charts).