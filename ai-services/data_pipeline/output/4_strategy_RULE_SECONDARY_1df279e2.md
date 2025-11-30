---
uuid: 1df279e2-f504-4465-ad77-cd9f1d5e8f0c
doc_type: smart_block
source_file: 1-AllDocuments (11).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: GENERAL_LEGAL
suggested_phase:
- step_4_strategy
topic_tags:
- Anbudsvillkor
- Förbehåll
- Alternativa anbud
entities: []
tags:
- anbud
- regel
- förkastande
- lou
constraints:
- param: alternative_bid
  operator: EQUALS
  value: false
  unit: null
  action: BLOCK
  error_msg: Alternativa anbud eller förbehåll är inte tillåtna.
---

# Regel: Förbud mot Alternativa Anbud
Anbudsgivaren får inte lämna sidoanbud, alternativa anbud eller reservera sig mot villkor i avropsförfrågan. Om detta görs kan anbudet komma att förkastas.