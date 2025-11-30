---
uuid: 82711cf6-c1a2-4040-b0ce-307510b6dd8b
doc_type: smart_block
source_file: 1-AllDocuments (9).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Geografisk omfattning
- Avropsområde
- Region
entities:
- Avropssvarsområde D
- Stockholms län
- Uppsala län
- Gotlands län
tags:
- exempel
- geografi
- region
- stockholm
- uppsala
- gotland
constraints:
- param: location
  operator: ONE_OF
  value:
  - Stockholms län
  - Uppsala län
  - Gotlands län
  action: BLOCK
  error_msg: Leveransorten måste vara inom Stockholms, Uppsala eller Gotlands län.
---

# Exempel: Geografisk Räckvidd
Denna avropsförfrågan riktades till samtliga leverantörer antagna på ramavtalet inom **Avropssvarsområde D**, vilket omfattade:

*   Stockholms län
*   Uppsala län
*   Gotlands län