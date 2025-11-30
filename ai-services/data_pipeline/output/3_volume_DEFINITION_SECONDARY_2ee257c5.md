---
uuid: 2ee257c5-9962-47e1-aff1-bb433017a8b6
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: DEFINITION
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
entities: []
tags:
- utvärdering
- pris
- kvalitet
- mervärdesavdrag
- takpris
constraints:
- param: hourly_rate
  operator: MAX
  value: 1200
  unit: sek
  action: BLOCK
  error_msg: Maximalt anbudspris är 1200 SEK/timme.
---

# Definition: Utvärderingsmodell (Pris och Kvalitet)
Anbud utvärderas baserat på det ekonomiskt mest fördelaktiga anbudet, där lägst utvärderingspris vinner. Ett takpris för anbudet är satt.

- **Formel:** Utvärderingspris = Timpris - Mervärdesavdrag (från intervju)
- **Maximalt timpris:** 1200 SEK
- **Maximalt mervärdesavdrag:** 600 SEK