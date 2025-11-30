---
uuid: 31a38f2a-32de-4b0c-ac3d-8fe03ee425de
doc_type: smart_block
source_file: 1-AllDocuments (28).pdf
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
- Distansarbete
- Resor
entities:
- Inera AB
- Lund
tags:
- närvaro
- kontor
- lund
- krav
- distansarbete
- hybridarbete
constraints:
- param: on_site_days_per_week
  operator: MIN
  value: 3
  unit: days
  action: BLOCK
  error_msg: Konsulten måste kunna arbeta på plats i Lund minst 3 dagar/vecka.
---

# Regel: Krav på Närvaro på Kontor (Exempel Lund)
För detta specifika uppdrag krävs det att konsulten är fysiskt på plats på beställarens kontor.

- **Plats:** Ineras kontor i Lund.
- **Närvarokrav:** Minst tre (3) dagar i veckan.
- **Ersättning:** Resor till och från kontoret i Lund ersätts ej av Inera.