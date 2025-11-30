---
uuid: 8f52d3a1-6a73-4941-96b1-b8ccdc753e27
doc_type: smart_block
source_file: 1-AllDocuments (31).pdf
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
- Systemutveckling
- Teknisk kompetens
entities:
- Senior Systemutvecklare
- Nivå 4
- C# / .Net Core
- Microsoft SQL
- REST
- React / Fluent UI
- Microsoft Graph API
- GIT
tags:
- ska_krav
- kompetens
- erfarenhet
- net_core
- sql
- git
- nivå_4
constraints:
- param: experience_csharp_dotnet
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Minst 3 års erfarenhet av C# / .Net Core krävs.
- param: experience_sql
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Minst 3 års erfarenhet av Microsoft SQL krävs.
- param: experience_rest_api
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Minst 3 års erfarenhet av REST-baserade WebAPI:er krävs.
- param: experience_ms_graph_api
  operator: MIN
  value: 6
  unit: months
  action: BLOCK
  error_msg: Minst 6 månaders erfarenhet av Microsoft Graph API krävs.
- param: experience_git
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Minst 3 års erfarenhet av GIT krävs.
---

# Regel: Specifika kompetenskrav (Ska-krav) för Senior Systemutvecklare
För rollen Senior Systemutvecklare (Nivå 4) i detta avrop ställs följande minimikrav på erfarenhet, vilket måste framgå av CV:

- **C# / .Net Core:** Minst 3 år
- **Microsoft SQL:** Minst 3 år
- **REST-baserade WebAPI:er:** Minst 3 år
- **GIT:** Minst 3 år
- **Microsoft Graph API:** Minst 6 månader
- **React / Fluent UI:** Erfarenhet krävs (ospecificerad tid)