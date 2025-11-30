---
uuid: bccb6c95-5683-42c9-ad6c-9b477cde43b2
doc_type: smart_block
source_file: 1-AllDocuments (32).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_3_volume
- step_4_strategy
topic_tags:
- Avropsomfattning
- Resursbehov
- Volymestimat
- Värdeestimat
- Avropsform
entities:
- Inera AB
- Senior Infrastrukturarkitekt
- IT-konsulttjänster 2021
- Förnyad Konkurrensutsättning
- Avropssvarsområde D
tags:
- exempel
- avrop
- inera
- fku
- senior_infrastrukturarkitekt
- it_konsulttjänster_2021
constraints:
- param: volume_hours
  operator: MAX
  value: 500
  unit: hours
  action: WARN
  error_msg: Uppskattad volym är 500 timmar, men detta kan variera.
- param: location
  operator: ONE_OF
  value:
  - Stockholms län
  - Uppsala län
  - Gotlands län
  action: BLOCK
  error_msg: Avropet gäller endast för leverantörer inom Avropssvarsområde D.
---

# Exempel: Avropsförfrågan för Senior Infrastrukturarkitekt (Inera)
Detta är ett exempel på en avropsförfrågan från Inera AB för en (1) resurskonsult i rollen som Senior Infrastrukturarkitekt. Avropet genomförs som en förnyad konkurrensutsättning (FKU) under ramavtalet IT-konsulttjänster 2021.

- **Volym:** Upp till 500 timmar (uppskattning).
- **Värde:** Uppskattat till 650 000 SEK.
- **Geografiskt Område:** Riktar sig till leverantörer inom Avropssvarsområde D (Stockholms län, Uppsala län, Gotlands län).