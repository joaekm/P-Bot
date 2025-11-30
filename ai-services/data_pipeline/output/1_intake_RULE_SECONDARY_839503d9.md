---
uuid: 839503d9-95f4-45ed-b643-19cb2bce8a0c
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
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
- Teknisk kompetens
- Språkkrav
entities:
- C#
- JavaScript
- SQL
- React
- Azure DevOps
- Git
- Microsoft System Center Configuration Manager
tags:
- ska_krav
- erfarenhet
- kompetens
- cv
constraints:
- param: experience_csharp_fullstack
  operator: MIN
  value: 84
  unit: months
  action: BLOCK
  error_msg: Kräver minst 7 års (84 månader) erfarenhet av fullstackutveckling i C#.
- param: experience_ms_sccm_integration
  operator: MIN
  value: 18
  unit: months
  action: BLOCK
  error_msg: Kräver minst 18 månaders erfarenhet av integration mot Microsoft SCCM.
---

# Regel: Obligatoriska Kompetenskrav (Ska-krav)
Offererad konsult SKA uppfylla följande minimikrav på erfarenhet, vilket ska styrkas i bifogat CV:
- **Minst 7 år:** Fullstackutveckling i C#, JavaScript, SQL, jQuery/React/Preact/Vue.
- **Minst 18 månader:** Integration mot Microsoft System Center Configuration Manager (SCCM).
- **God kunskap:** Visual Studio, Azure DevOps, Git, REST API-integration.
- **Språk:** Svenska och engelska i tal och skrift.