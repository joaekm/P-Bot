---
uuid: 96ae6765-6caa-4ed0-bbde-41205f7b6252
doc_type: smart_block
source_file: 1-AllDocuments (6).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Utvärderingsmodell
- Prisutvärdering
- Kvalitetsutvärdering
- Takpris
- Mervärde
entities:
- Utvärderingspris
tags:
- exempel
- utvärdering
- pris_kvalitet
- takpris
- fku
constraints:
- param: hourly_rate
  operator: MAX
  value: 1150
  unit: sek
  action: BLOCK
  error_msg: Anbudspriset får inte överstiga 1150 SEK/timme.
---

# Exempel: Utvärderingsmodell (Pris & Kvalitet)
Detta exempel visar en utvärderingsmodell där det ekonomiskt mest fördelaktiga anbudet antas baserat på en kombination av pris och kvalitet.

- **Maximalt anbudspris:** 1150 SEK/timme.
- **Kvalitetsutvärdering:** Sker via intervju, där poäng ger ett 'mervärdesavdrag' på priset.
- **Formel:** `Anbudspris - Mervärdesavdrag = Utvärderingspris`.
- **Vinnare:** Anbudet med lägst utvärderingspris.