---
uuid: da7c3b62-887f-45ef-a5e0-a09d172777d7
doc_type: smart_block
source_file: allmanna-kontraktsvillkor-fornyad-konkurrensutsattning---it-konsulttjanster-2021-2025-11-21.docx
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Vite
- Sanktioner
- Försening
- Avtalsbrott
entities: []
tags:
- vite
- försening
- sanktion
- avtalsbrott
constraints:
- param: penalty_fee_delay_percent_per_week
  operator: MAX
  value: 3
  unit: percent
  action: BLOCK
  error_msg: Vitesnivån vid försening får ej överstiga 3% per vecka.
- param: penalty_fee_duration_weeks
  operator: MAX
  value: 5
  unit: weeks
  action: INFO
  error_msg: Vite kan som standard utgå i maximalt 5 veckor.
---

# Regel: Vite vid Försening
**Standardregel:** Om avtalad leveransdag passeras har myndigheten rätt till vite med 1% av kontraktets ersättning för varje påbörjad vecka. Vitet utgår i maximalt 5 veckor.
**Avropsregel:** Myndigheten kan i avropet ange en högre vitesnivå, dock maximalt 3% per vecka.