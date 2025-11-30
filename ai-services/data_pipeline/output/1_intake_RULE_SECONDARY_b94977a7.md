---
uuid: b94977a7-a1bf-48e1-9613-b65fd3316a81
doc_type: smart_block
source_file: 1-AllDocuments (23).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Placeringsort
- Distansarbete
- Närvarokrav
entities:
- Inera
- Lund
tags:
- exempel
- regel
- närvaro
- lund
- arbetsplats
- krav
constraints:
- param: on_site_presence_days_per_week
  operator: MIN
  value: 3
  unit: days
  action: WARN
  error_msg: Konsulten måste kunna vara på plats i Lund minst 3 dagar/vecka vid behov.
---

# Regel: Krav på närvaro på plats
**KONTROLLERA** att offererad konsult kan uppfylla krav på fysisk närvaro.

**Exempelregel:**
Konsulten förväntas på begäran ha möjlighet att infinna sig på plats på beställarens kontor (ex: Lund) minst tre (3) dagar i veckan.