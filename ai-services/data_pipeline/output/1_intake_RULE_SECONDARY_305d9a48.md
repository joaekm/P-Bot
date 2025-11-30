---
uuid: 305d9a48-de16-47cf-9662-a1adcb3bc555
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Placeringsort
- Närvarokrav
- Arbetsplats
entities:
- Lund
- Inera
tags:
- plats
- närvaro
- lund
- kontor
constraints:
- param: on_site_presence_days_per_week
  operator: MIN
  value: 3
  unit: days
  action: BLOCK
  error_msg: Konsulten förväntas vara på plats i Lund minst tre dagar i veckan.
- param: location
  operator: EQUALS
  value: Lund
  action: BLOCK
  error_msg: Arbetsplatsen är Ineras kontor i Lund.
---

# Regel: Krav på Plats och Närvaro
Konsulten förväntas arbeta på plats vid beställarens (Ineras) kontor i Lund minst tre (3) dagar i veckan. Veckovisa avstämningar sker antingen digitalt eller på plats i Lund.