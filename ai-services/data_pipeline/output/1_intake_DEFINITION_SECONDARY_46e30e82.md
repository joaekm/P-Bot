---
uuid: 46e30e82-2dd9-49e3-807e-653a2a544eb9
doc_type: smart_block
source_file: 1-AllDocuments (24).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Geografisk avgränsning
- Avropsområde
entities:
- Avropssvarsområde G
- Skåne län
- Blekinge län
- Kronobergs län
tags:
- geografi
- region
- skåne
- blekinge
- kronoberg
constraints:
- param: location
  operator: ONE_OF
  value:
  - Skåne län
  - Blekinge län
  - Kronobergs län
  action: BLOCK
  error_msg: Leverantören måste tillhöra Avropssvarsområde G (Skåne, Blekinge, Kronoberg).
---

# Definition: Geografiskt avropsområde
Denna avropsförfrågan riktar sig endast till leverantörer som är antagna på Ramavtalet inom Avropssvarsområde G.

- **Godkända län:** 
  - Skåne län
  - Blekinge län
  - Kronobergs län