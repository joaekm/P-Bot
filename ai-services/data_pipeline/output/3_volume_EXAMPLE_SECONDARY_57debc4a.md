---
uuid: 57debc4a-0f12-4ec7-b111-9e3fe2821a36
doc_type: smart_block
source_file: 1-AllDocuments (17).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Utvärderingsmodell
- Prisutvärdering
- Kvalitetsutvärdering
- Mervärdesavdrag
- Takpris
entities:
- Utvärderingspris
tags:
- utvärdering
- pris
- kvalitet
- mervärde
- formel
- takpris
constraints:
- param: hourly_rate
  operator: MAX
  value: 1200
  unit: sek
  action: BLOCK
  error_msg: Maximalt anbudspris är 1200 SEK/timme.
---

# Exempel: Utvärderingsmodell med pristak och mervärdesavdrag
En utvärderingsmodell där det ekonomiskt mest fördelaktiga anbudet utvärderas baserat på pris och kvalitet.
- **Formel:** `Anbudspris - Mervärdesavdrag = Utvärderingspris`
- **Maximalt anbudspris:** 1200 kr/timme
- **Maximalt mervärdesavdrag:** 600 kr