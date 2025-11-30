---
uuid: 21c031e0-4fbd-488c-9715-570986d8aee6
doc_type: smart_block
source_file: 1-AllDocuments (28).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Kompetenskrav
- Erfarenhetskrav
- Teknisk specifikation
- Rollbeskrivning
entities:
- Senior Systemutvecklare
- Nivå 5
- C#
- .Net Core
- SQL
- Microsoft Graph API
- GIT
- React
tags:
- kravspecifikation
- nivå_5
- senior
- systemutvecklare
- csharp
- dotnet
- erfarenhet
- cv_krav
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Offererad konsult ska vara på Nivå 5.
- param: experience_years_systemutveckling
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av systemutveckling i C#/.Net/SQL.
- param: experience_years_git
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Kräver minst 3 års erfarenhet av GIT.
- param: experience_years_ms_graph_api
  operator: MIN
  value: 1
  unit: years
  action: BLOCK
  error_msg: Kräver minst 1 års erfarenhet av Microsoft Graph API.
---

# Definition: Kompetenskrav Senior Systemutvecklare (Nivå 5)
Specifika kompetenskrav för rollen Senior Systemutvecklare, Nivå 5, i ett avrop från Inera.

**Erfarenhetskrav (minst):**
- **5 år:** Systemutveckling i C# / .Net Core, SQL, och integration med REST-baserade WebAPI:er.
- **3 år:** Arbete med GIT som versionshanterare.
- **1 år:** Arbete med Microsoft Graph API.

**Djup kunskap i:**
- Visual Studio
- TypeScript
- React / Fluent UI