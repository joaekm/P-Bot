---
uuid: 473cb620-d1fd-467d-9c6f-9d4e7cc072fe
doc_type: smart_block
source_file: kontraktsvillkor-dynamisk-rangordning---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_4_strategy
topic_tags:
- Immateriella rättigheter
- Uppdragsresultat
- Nyttjanderätt
- Äganderätt
entities: []
tags:
- ipr
- äganderätt
- nyttjanderätt
- avropsvillkor
- standardvillkor
constraints:
- param: ipr_choice
  operator: ONE_OF
  value:
  - full_ownership
  - exclusive_use
  - non_exclusive_use
  action: WARN
  error_msg: Ett val för rätt till uppdragsresultat måste anges. Om inget anges gäller
    alternativ b) som standard.
---

# Regel: Rätt till uppdragsresultat (IPR)
Vid avrop SKA den upphandlande myndigheten ange vilken rätt till uppdragsresultatet som behövs. Valbara alternativ är:
- **a)** Full och oinskränkt äganderätt.
- **b)** Exklusiv, vederlagsfri och obegränsad nyttjanderätt.
- **c)** Icke-exklusiv, vederlagsfri och obegränsad nyttjanderätt.

**STANDARDREGEL:** Om inget alternativ anges, gäller automatiskt alternativ **b)**.