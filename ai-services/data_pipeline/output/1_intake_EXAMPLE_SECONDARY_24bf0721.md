---
uuid: 24bf0721-96c4-4eef-8c90-3de3cacb043c
doc_type: smart_block
source_file: 1-AllDocuments (20).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Erfarenhetskrav
- Kompetenskrav
- Avtalshantering
- Offentlig sektor
entities:
- RIV-TA
- CV
tags:
- exempel
- inera
- ska_krav
- erfarenhet
- riv_ta
- offentliga_avtal
constraints:
- param: experience_years_contract_management
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Kräver minst 3 års erfarenhet av avtalshantering.
- param: experience_years_public_contracts
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Kräver minst 3 års erfarenhet av offentliga avtal.
---

# Exempel: Obligatoriska Erfarenhetskrav (Inera)
Offererad konsult ska uppfylla följande obligatoriska erfarenhetskrav:
*   Minst tre (3) års erfarenhet av framtagning, implementation och justering av avtal.
*   Minst tre (3) års erfarenhet av uppföljning och kravställning av offentliga avtal.
*   Erfarenhet som ansvarig för uppdrag inom RIV-TA med koppling till kundavtal och personuppgiftshantering.
*   Erfarenhet av att driva nationella projekt inom hälso- och sjukvård inom RIV-TA.