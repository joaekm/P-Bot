---
uuid: d0095c3d-4b99-4422-83c2-de064bd04c22
doc_type: smart_block
source_file: 1-AllDocuments (30).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Takpris
- Timpris
- Prissättning
- Budget
entities: []
tags:
- takpris
- timpris
- anbudspris
- kostnad
constraints:
- param: hourly_rate
  operator: MAX
  value: 1300
  unit: sek
  action: BLOCK
  error_msg: Timpriset får ej överstiga det angivna takpriset på 1300 SEK.
---

# Regel: Takpris i Avrop
I Ineras avrop specificerades ett takpris per timme och konsultroll på **1300 SEK**. Anbud med timpris som överstiger detta belopp kommer att förkastas. Alla kringkostnader såsom resor, logi och traktamente ska inkluderas i timpriset.