---
uuid: aaee1899-85f9-43e9-a5ff-f0a87f484ce0
doc_type: smart_block
source_file: 1-AllDocuments (11).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_3_volume
topic_tags:
- Volymestimat
- Optionsrätt
- Avropsomfattning
- Resursuppdrag
entities:
- Inera AB
tags:
- volym
- timmar
- option
- estimat
- exempel
constraints:
- param: volume_hours
  operator: MAX
  value: 400
  unit: hours
  action: WARN
  error_msg: Initial avtalsperiod omfattar upp till 400 timmar.
- param: option_volume_hours
  operator: MAX
  value: 550
  unit: hours
  action: WARN
  error_msg: Optionen omfattar ytterligare upp till 550 timmar.
---

# Exempel: Volymspecifikation med Option
Uppdraget omfattar initialt upp till 400 timmar. Det finns en option på förlängning med ytterligare 550 timmar. Angivna timmar är en uppskattning och inga volymer garanteras.