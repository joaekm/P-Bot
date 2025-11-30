---
uuid: e068629b-0759-412c-b8bb-a6e0a9fc6790
doc_type: smart_block
source_file: avropsvagledning---it-konsulttjanster-2021-2025-11-21.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Prissättning
- Takpris
- Avropsform
- Kompetensnivå
entities:
- Förnyad Konkurrensutsättning
- Nivå 1
- Nivå 2
- Nivå 3
- Nivå 4
tags:
- takpris
- fku
- pris
- offert
constraints:
- param: hourly_rate
  operator: MAX
  value: framework_price
  unit: sek
  action: BLOCK
  error_msg: Offererat timpris för nivå 1-4 får ej överstiga ramavtalets takpris.
---

# Regel: Prissättning vid FKU (Nivå 1-4)
**OM** avrop sker via Förnyad Konkurrensutsättning (FKU) för kompetensnivå 1, 2, 3 eller 4:
**DÅ** gäller ramavtalets timpriser som **TAKPRISER**.

**KONTROLLERA:** Leverantörens offererade timpris får vara lägre än, men ALDRIG högre än, det fastställda priset i ramavtalet.