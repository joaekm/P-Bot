---
uuid: a7cd1062-33bd-4125-90ab-e31fd36c7420
doc_type: smart_block
source_file: Upphandlingsdokument (GDPR).pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Antal leverantörer
- Ramavtalsstruktur
- Konkurrens
- Anbudsområde
entities:
- IT-konsulttjänster 2021
- Anbudsområde
tags:
- antal_leverantörer
- ramavtal
- strategi
- 8_leverantörer
constraints:
- param: supplier_count_per_area
  operator: MAX
  value: 8
  unit: suppliers
  action: INFO
  error_msg: Målet är att anta åtta (8) leverantörer per anbudsområde.
---

# Regel: Antal Ramavtalsleverantörer
**MÅL:** Adda kommer att anta upp till **åtta (8)** anbudsgivare per anbudsområde. Detta förutsätter att tillräckligt många kvalificerade anbud inkommer.