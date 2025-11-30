---
uuid: aff5fe48-e91e-4359-a227-de0435c18555
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
- Ansvarsbegränsning
- Skadestånd
- Försäkring
entities: []
tags:
- ansvar
- skadestånd
- ansvarsbegränsning
- försäkring
constraints:
- param: liability_personal_property_per_incident
  operator: MAX
  value: 10000000
  unit: sek
  action: INFO
  error_msg: Ansvarsbegränsning för person/sakskada är 10 MSEK per skada.
- param: liability_personal_property_per_year
  operator: MAX
  value: 20000000
  unit: sek
  action: INFO
  error_msg: Ansvarsbegränsning för person/sakskada är 20 MSEK per år.
- param: liability_financial_loss_per_incident_year
  operator: MAX
  value: 5000000
  unit: sek
  action: INFO
  error_msg: Ansvarsbegränsning för ren förmögenhetsskada är 5 MSEK per skada och
    år.
---

# Regel: Ansvarsbegränsning för leverantör
Leverantörens skadeståndsansvar är begränsat enligt följande:
- **Person- eller sakskada:** Max 10 MSEK per skada och 20 MSEK per år.
- **Annan ren förmögenhetsskada:** Max 5 MSEK per skada och 5 MSEK per år.

**UNDANTAG:** Begränsningarna gäller ej vid grov vårdslöshet eller uppsåt.