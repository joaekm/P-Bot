---
uuid: bb281469-6b7d-4fb0-860a-840fb780cc60
doc_type: smart_block
source_file: Upphandlingsdokument (GDPR).pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Svarstid
- Tidsfrist
- Avropsprocess
entities:
- Dynamisk Rangordning
tags:
- svarstid
- dynamisk_rangordning
- dr
- 2_dagar
- tidsfrist
constraints:
- param: response_time_days_dr
  operator: MAX
  value: 2
  unit: workdays
  action: WARN
  error_msg: Standard-svarstiden för Dynamisk Rangordning är 2 arbetsdagar. Längre
    tid kan anges i avropet.
---

# Regel: Svarstid vid Dynamisk Rangordning
**KRAV:** Leverantör MÅSTE svara på en avropsförfrågan via Dynamisk Rangordning inom **två (2) arbetsdagar**.

**UNDANTAG:** Den upphandlande myndigheten kan ange en längre svarstid i förfrågan.