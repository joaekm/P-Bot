---
uuid: f80d82e4-cde5-43d0-a456-d0923cd95b5c
doc_type: smart_block
source_file: 1-AllDocuments (32).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Anbudsvillkor
- Reservationer
- Anbudsgiltighet
entities: []
tags:
- regel
- förbud
- sidoanbud
- reservation
constraints:
- param: alternative_bid
  operator: EQUALS
  value: false
  action: BLOCK
  error_msg: Alternativa anbud eller reservationer är ej tillåtna.
---

# Regel: Förbud mot Alternativa Anbud och Reservationer
**ÅTGÄRD:** KONTROLLERA ATT anbudet inte innehåller sidoanbud, alternativa anbud eller reservationer mot villkoren i avropsförfrågan.
**KONSEKVENS:** Om sådana förekommer kan anbudet förkastas.