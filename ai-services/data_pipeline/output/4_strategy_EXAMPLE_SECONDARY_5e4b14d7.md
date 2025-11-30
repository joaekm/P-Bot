---
uuid: 5e4b14d7-81c7-4d6c-847d-59af82c197b3
doc_type: smart_block
source_file: 1-AllDocuments (20).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_4_strategy
- step_3_volume
topic_tags:
- Utvärderingsmodell
- Takpris
- Prisutvärdering
- FKU
entities:
- Inera AB
tags:
- exempel
- fku
- utvärdering
- takpris
- pris
constraints:
- param: hourly_rate
  operator: MAX
  value: 1500
  unit: sek
  action: BLOCK
  error_msg: Maximalt tillåtet timpris är 1500 SEK.
---

# Exempel: Utvärderingsmodell med Takpris (Inera)
Inera kommer anta det ekonomiskt mest fördelaktiga anbudet baserat på pris och kvalitet. Ett maximalt anbudspris på 1500 SEK per timme är satt. Anbud med högre timpris kommer att förkastas.

**Utvärderingsformel:**
`Utvärderingspris = Anbudspris - Fiktivt mervärdesavdrag`