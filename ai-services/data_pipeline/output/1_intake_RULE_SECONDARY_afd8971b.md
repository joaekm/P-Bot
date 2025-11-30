---
uuid: afd8971b-ae93-4bbd-95c2-7c3bff39ca62
doc_type: smart_block
source_file: 1-AllDocuments (29).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Tillgänglighet
- Inställelsetid
- Placeringsort
- Arbetsplats
entities:
- Stockholm
tags:
- tillgänglighet
- startdatum
- stockholm
- platsnärvaro
constraints:
- param: availability_days_after_signing
  operator: MAX
  value: 3
  unit: workdays
  action: BLOCK
  error_msg: Konsulten måste vara tillgänglig inom 3 arbetsdagar.
- param: on_site_days_per_month
  operator: MAX
  value: 4
  unit: days
  action: WARN
  error_msg: Förväntad närvaro på plats är upp till 4 dagar/månad.
---

# Regel: Tillgänglighet och Placering
Offererad konsult måste finnas tillgänglig per omgående och senast inom **tre (3) arbetsdagar** från kontraktssignering. Konsulten förväntas kunna infinna sig på plats på Ineras kontor i Stockholm på förfrågan, upp till **fyra (4) dagar i månaden**.