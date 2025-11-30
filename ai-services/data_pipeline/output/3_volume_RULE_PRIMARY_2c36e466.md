---
uuid: 2c36e466-c68f-492d-bb81-64bb26fa6f1f
doc_type: smart_block
source_file: kontraktsvillkor-dynamisk-rangordning---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Prisjustering
- Timpris
- Övertidsersättning
- Obekväm arbetstid
entities: []
tags:
- övertid
- ersättning
- timpris
- ob_tillägg
constraints:
- param: overtime_rate_evening
  operator: EQUALS
  value: 1.5
  unit: multiplier
  action: INFO
  error_msg: Timpriset multipliceras med 1.5 för tidig morgon/kväll vardagar.
- param: overtime_rate_night_weekend
  operator: EQUALS
  value: 2.0
  unit: multiplier
  action: INFO
  error_msg: Timpriset multipliceras med 2.0 för natt och helg.
---

# Regel: Ersättning för obekväm arbetstid
Normal arbetstid är helgfria vardagar kl. 07:00-19:00. För arbete utanför denna tid gäller:
- **OB 1 (x1.5):** Vardagar kl. 06:00-07:00 och 19:00-21:00.
- **OB 2 (x2.0):** Vardagar kl. 21:00-06:00 samt all tid under helger.