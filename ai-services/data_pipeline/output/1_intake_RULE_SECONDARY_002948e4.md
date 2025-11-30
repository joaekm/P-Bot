---
uuid: 002948e4-8b0c-401e-9d8c-e7ecabf28bd0
doc_type: smart_block
source_file: 1-AllDocuments (24).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Kompetenskrav
- Erfarenhetskrav
- Certifieringskrav
- Rollbeskrivning
entities:
- Senior Enterprisearkitekt
- Nivå 5
- Azure DevOps
- Git
- SCRUM Master
- Zero Trust
- IAM
tags:
- ska_krav
- nivå_5
- senior_enterprisearkitekt
- erfarenhet
- certifiering
- cv
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult måste vara på Nivå 5.
- param: experience_years
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Minst 5 års erfarenhet krävs för flera specificerade områden.
- param: certification
  operator: ONE_OF
  value:
  - SCRUM Master
  action: BLOCK
  error_msg: Giltigt SCRUM Master certifikat måste bifogas.
---

# Regel: Kravspecifikation för Senior Enterprisearkitekt (Nivå 5)
Offererad konsult för rollen Senior Enterprisearkitekt måste uppfylla samtliga krav för Nivå 5 enligt ramavtalet och följande specifika erfarenhetskrav. CV och certifikat måste bifogas som bevis.

### Erfarenhetskrav (minst 5 år):
- Visual Studio
- Azure DevOps
- Git
- Integrera med REST-baserade WebAPI:er
- Ansvar för utveckling/implementering av IT-processer & livscykelhantering
- Leda utveckling av lösningar, processer & förändringsprojekt
- Arbete med IT-infrastruktur & stora klientmiljöer (privat/offentlig)
- Kravfångst (självständigt)
- Leda workshops för kravfångst (minst 5 pers)

### Erfarenhetskrav (minst 3 år):
- Klientplattformskomponenter (ePaket, Overview, Automation eller motsv.)
- IT-infrastruktur & klientmiljöer med fokus på Zero Trust & IAM
- Microsoft Azure DevOps
- GIT som versionshanterare

### Certifieringskrav:
- SCRUM Master