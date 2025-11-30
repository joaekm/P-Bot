---
uuid: edad6e6f-23ac-4ed4-8b97-712ddb21af8c
doc_type: smart_block
source_file: 1-AllDocuments (22).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Geografiskt område
- Avropsområde
- Leverantörskvalificering
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
  unit: null
  action: BLOCK
  error_msg: Leverantören måste tillhöra avropsområde G (Skåne, Blekinge, Kronoberg).
---

# Regel: Geografiskt Avropsområde
Avropsförfrågan riktas uteslutande till leverantörer som är antagna på ramavtalet inom Avropssvarsområde G, vilket omfattar Skåne län, Blekinge län och Kronobergs län.