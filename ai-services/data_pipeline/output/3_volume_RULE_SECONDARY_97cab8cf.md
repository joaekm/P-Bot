---
uuid: 97cab8cf-c81a-424a-9d77-1f2d37caf86a
doc_type: smart_block
source_file: 1-AllDocuments (8).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_3_volume
topic_tags:
- Avtalsförlängning
- Notifiering
- Tidsfrist
- Avtalsvillkor
entities: []
tags:
- option
- förlängning
- tidsfrist
constraints:
- param: extension_notification_days_before_expiry
  operator: MIN
  value: 28
  unit: days
  action: WARN
  error_msg: Notifiering om förlängning bör ske minst 4 veckor (28 dagar) innan avtalets
    slut.
---

# Regel: Tidsfrist för notifiering om förlängning
Beställaren ska meddela om en optionsförlängning ska nyttjas senast fyra (4) veckor innan det befintliga avtalet löper ut.