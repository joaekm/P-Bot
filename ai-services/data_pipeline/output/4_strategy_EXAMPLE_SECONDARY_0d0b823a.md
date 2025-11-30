---
uuid: 0d0b823a-b3a3-4015-84a0-a32d2bfc1dc9
doc_type: smart_block
source_file: 1-AllDocuments (9).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Utvärderingsmodell
- Mervärdesavdrag
- Kvalitetsutvärdering
- Prisutvärdering
entities: []
tags:
- exempel
- utvärdering
- mervärde
- kvalitet
- pris
constraints:
- param: quality_score_total
  operator: MIN
  value: 5
  unit: points
  action: BLOCK
  error_msg: Anbud med 4 poäng eller lägre förkastas.
---

# Exempel: Utvärderingsmodell med Mervärdesavdrag
Anbudet utvärderades baserat på det ekonomiskt mest fördelaktiga anbudet enligt modellen Pris och Kvalitet.

**Formel:** `Anbudspris (timpris) - Mervärdesavdrag = Utvärderingspris`

Kvalitet bedömdes via intervju där poäng (0-12 totalt) genererade ett fiktivt avdrag på priset. Varje poäng var värd 50 kr i avdrag, med ett maximalt avdrag på 600 kr. Anbud med en totalpoäng på 4 eller lägre förkastades.