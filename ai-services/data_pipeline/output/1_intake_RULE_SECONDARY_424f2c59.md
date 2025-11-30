---
uuid: 424f2c59-c301-4a39-8633-89020ec87ca1
doc_type: smart_block
source_file: 1-AllDocuments (31).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Arbetsplats
- Närvarokrav
- Resor
- Kostnader
entities:
- Inera
- Lund
tags:
- plats
- närvaro
- lund
- resekostnad
constraints:
- param: on_site_presence_days_per_week
  operator: MIN
  value: 3
  unit: days
  action: BLOCK
  error_msg: Konsulten måste kunna arbeta på plats i Lund minst 3 dagar i veckan.
---

# Regel: Krav på Platsnärvaro
Konsulten förväntas arbeta på plats på Ineras kontor i Lund minst tre (3) dagar i veckan. Beställaren ersätter inte resekostnader till och från detta kontor, då det betraktas som ordinarie arbetsplats. Andra tjänsteresor som beställs av Inera ersätts enligt policy.