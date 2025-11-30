---
uuid: 3469a92b-33a7-4bc5-850e-f3736446c11f
doc_type: smart_block
source_file: 1-AllDocuments (19).pdf
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
- Inera
- Stockholm
tags:
- stockholm
- närvaro
- platsbunden
- krav
constraints:
- param: location
  operator: EQUALS
  value: Stockholm
  unit: null
  action: BLOCK
  error_msg: Uppdraget kräver närvaro i Stockholm.
- param: on_site_presence_days_per_week
  operator: EQUALS
  value: 3
  unit: days
  action: WARN
  error_msg: Beställaren kräver närvaro på plats 3 dagar per vecka.
---

# Regel: Närvarokrav på plats (Exempel)
I Ineras avrop för Transformationsledare ställdes krav på fysisk närvaro.

**KRAV:** Konsulten förväntas infinna sig på plats i Ineras lokaler i Stockholm tre (3) arbetsdagar per vecka.