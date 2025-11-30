---
uuid: 12d377fc-aa32-4476-9088-f2e9795e1dc3
doc_type: smart_block
source_file: 1-AllDocuments (17).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Erfarenhetskrav
- Teknisk kompetens
- Ska-krav
- Kravspecifikation
entities:
- C#
- JavaScript
- SQL
- Microsoft System Center Configuration Manager
- Azure DevOps
tags:
- ska_krav
- erfarenhet
- kompetenskrav
- fullstack
constraints:
- param: experience_years_fullstack
  operator: MIN
  value: 7
  unit: years
  action: BLOCK
  error_msg: Kräver minst 7 års erfarenhet av fullstackutveckling.
- param: experience_months_mscsm
  operator: MIN
  value: 18
  unit: months
  action: BLOCK
  error_msg: Kräver minst 18 månaders erfarenhet av integration mot Microsoft System
    Center Configuration Manager.
---

# Exempel: Tekniska ska-krav för konsult
Ett exempel på specifika, mätbara erfarenhetskrav (ska-krav) för en roll:
- **Minst 7 års erfarenhet** av fullstackutveckling (C#, JavaScript, SQL, etc.).
- **Minst 18 månaders erfarenhet** av integration mot Microsoft System Center Configuration Manager.
- God kunskap om specificerade verktyg (Visual Studio, Azure DevOps, Git).
- Språkkunskaper i svenska och engelska.