---
uuid: 1f4e76f7-c0c7-46df-a779-1d1f094c5bd7
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
- Vite
- Försening
- Sanktion
- Kontraktsbrott
entities: []
tags:
- vite
- försening
- sanktion
- straffavgift
constraints:
- param: penalty_delay_rate
  operator: EQUALS
  value: 0.01
  unit: percent_per_week
  action: INFO
  error_msg: Vite vid försening är 1% per påbörjad vecka.
- param: penalty_delay_duration
  operator: MAX
  value: 5
  unit: weeks
  action: INFO
  error_msg: Vite utgår i maximalt 5 veckor.
---

# Regel: Vite vid försening
**OM** leverans sker efter avtalad leveransdag:
**DÅ** har den upphandlande myndigheten rätt till vite.
- **Belopp:** 1% av kontraktets ersättning per påbörjad vecka.
- **Maxtak:** Vitet utgår som längst under 5 veckor.