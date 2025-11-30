---
uuid: 48ab540f-3606-438c-b96d-5fc334aa90ec
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Prissättning
- Valuta
- Tilläggskostnader
- Fasta priser
entities: []
tags:
- pris
- sek
- moms
- fasta_priser
- tilläggskostnader
constraints:
- param: currency
  operator: EQUALS
  value: SEK
  action: BLOCK
  error_msg: Alla priser måste anges i SEK.
- param: additional_costs
  operator: EQUALS
  value: 0
  unit: sek
  action: BLOCK
  error_msg: Inga tilläggskostnader för resor, traktamente etc. accepteras.
---

# Regel: Prissättning och Ersättning
Alla priser SKA anges i svenska kronor (SEK) exklusive mervärdesskatt. Angivna priser är fasta och ska inkludera samtliga kostnader (resor, logi, administration etc.). Inga tilläggskostnader accepteras.