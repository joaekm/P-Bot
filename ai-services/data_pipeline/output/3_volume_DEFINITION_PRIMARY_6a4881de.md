---
uuid: 6a4881de-4c70-4b40-8fa3-33e26fd02e88
doc_type: smart_block
source_file: avropsvagledning---it-konsulttjanster-2021-2025-11-21.pdf
authority_level: PRIMARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Giltighetstid
entities:
- IT-konsulttjänster 2021
tags:
- avtalsperiod
- år_2022
- år_2026
- september_26
- september_25
constraints:
- param: contract_award_date
  operator: MAX
  value: '2026-09-25'
  unit: date
  action: BLOCK
  error_msg: Kontrakt kan inte tilldelas efter att ramavtalet har löpt ut (2026-09-25).
---

# Definition: Avtalsperiod
Ramavtalet `IT-konsulttjänster 2021` gäller i fyra år.

*   **Startdatum:** 2022-09-26
*   **Slutdatum:** 2026-09-25

Kontrakt måste tilldelas innan ramavtalets slutdatum, men tjänster kan levereras efter att ramavtalet har löpt ut.