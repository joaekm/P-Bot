---
uuid: 5b7a6cdc-03cf-4b50-b820-c5fe0bb70288
doc_type: smart_block
source_file: 1-AllDocuments (11).pdf
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
- Kompetenskrav
- Offentlig sektor
- CV-krav
entities:
- NTJP
- SOAP
- Patientdatalagen
tags:
- skallkrav
- erfarenhet
- cv
- kompetens
- exempel
constraints:
- param: experience_public_sector_change_lead
  operator: MIN
  value: 1
  unit: years
  action: BLOCK
  error_msg: Kräver minst 1 års erfarenhet av ledarskap i offentlig sektor.
- param: experience_ntjp
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av NTJP eller motsvarande.
---

# Exempel: Specifika Erfarenhetskrav (Ska-krav)
För att kvalificera sig måste den offererade konsulten uppfylla flera specifika erfarenhetskrav, angivna i antal år. CV ska bifogas som tydligt påvisar att kraven är uppfyllda.
- Minst 1 års erfarenhet av utbildning/ledning inom offentlig sektor.
- Minst 2 års erfarenhet av NTJP eller motsvarande.
- Minst 1 års erfarenhet av Samverkansarkitektur/SOAP.
- Minst 1 års erfarenhet som IT-arkitekt/processledare inom offentlig sektor.
- Minst 1 års erfarenhet av patientdatalagen.