---
uuid: a14c4fec-d984-4cf1-8ca6-05561d672edd
doc_type: smart_block
source_file: 1-AllDocuments (29).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Referenskrav
- Kvalificering
- Beviskrav
entities:
- Bilaga 1
- MongoDB
tags:
- referens
- kvalificering
- ska_krav
constraints:
- param: reference_project_age_years
  operator: MAX
  value: 3
  unit: years
  action: BLOCK
  error_msg: Referensuppdrag får inte vara äldre än 3 år.
---

# Regel: Krav på Referensuppdrag
Anbudsgivare ska redovisa referensuppdrag i Bilaga 1. Samtliga referensuppdrag får vara pågående och **inte äldre än tre (3) år** från sista anbudsdag.

**Krav på referenser:**
- **a) Konsumentmigrering:** Minst ett uppdrag som omfattat migrering av ett större system med >50 kunder.
- **b) Teknisk projektledning:** Minst ett uppdrag som ledande/biträdande för ett tekniskt projekt med databaser (ex. MongoDB) och test/testledning.