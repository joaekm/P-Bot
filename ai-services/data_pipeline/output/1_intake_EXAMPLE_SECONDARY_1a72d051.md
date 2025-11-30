---
uuid: 1a72d051-4fb9-43c8-a60a-d893c9a756b8
doc_type: smart_block
source_file: 1-AllDocuments (23).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Rollprofil
- Kravspecifikation
- Kompetenskrav
- Erfarenhetskrav
entities:
- Senior Mjukvaruarkitekt
- Nivå 5
- Inera
- E-klient
- Microsoft Endpoint Manager
- Azure DevOps
- IT-konsulttjänster 2021
tags:
- exempel
- kravspecifikation
- ska_krav
- senior_mjukvaruarkitekt
- nivå_5
- fullstack
- microsoft
- erfarenhetskrav
constraints:
- param: competence_level
  operator: EQUALS
  value: 5
  unit: level
  action: BLOCK
  error_msg: Konsulten måste uppfylla kraven för Nivå 5 enligt ramavtalet.
- param: experience_fullstack_csharp_js_sql_jquery
  operator: MIN
  value: 7
  unit: years
  action: BLOCK
  error_msg: Kräver minst 7 års erfarenhet av fullstackutveckling (C#, JavaScript,
    SQL, jQuery).
- param: experience_microsoft_endpoint_manager
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av utvecklingsprojekt relaterade till Microsoft
    Endpoint Manager/Configuration Manager.
- param: experience_react_fluentui
  operator: MIN
  value: 1
  unit: years
  action: BLOCK
  error_msg: Kräver minst 1 års erfarenhet av React och FluentUI.
- param: experience_azure_devops_git
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Kräver minst 3 års erfarenhet av Azure DevOps och GIT.
---

# Exempel: Detaljerad kravspecifikation för Senior Mjukvaruarkitekt (Nivå 5)
Detta är ett exempel på en kravspecifikation från ett avrop inom ramavtalet IT-konsulttjänster 2021. Kraven är uppdelade i erfarenhetsår och specifik kunskap.

**Grundkrav:**
- **Nivå:** Offererad konsult SKA vara på Nivå 5 enligt ramavtalet.

**Erfarenhetskrav (år):**
- **7+ år:** Fullstackutveckling (C#, JavaScript, SQL, jQuery).
- **5+ år:** Utveckling av stödverktyg för Microsoft Endpoint/Configuration Manager.
- **5+ år:** Utveckling för klienthantering (C# och C++).
- **5+ år:** Klientinfrastruktur för regioner/kommuner.
- **5+ år:** Klientplattformskomponenter (specifikt Sysman).
- **5+ år:** JavaScript, .Net Framework/.Net Core, SQL, och integration mot SCCM.
- **3+ år:** Microsoft Azure DevOps och GIT.
- **1+ år:** React och FluentUI.

**Kunskapskrav:**
- Djup kunskap i Visual Studio, Azure DevOps, Git och REST-baserade WebAPI-integrationer.