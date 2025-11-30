---
uuid: 96b9f395-c669-4298-a4fb-7bfa6b1fadc0
doc_type: smart_block
source_file: mall-for-avropsforfragan-resursuppdrag-fornyad-konkurrensutsattning---it-konsulttjanster-2021.docx
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_2_level
topic_tags:
- Takpris
- Prissättning
- Kompetensnivå
- Avropsvillkor
entities:
- Nivå 1-4
- Nivå 5
- Bilaga B
tags:
- takpris
- pris
- regel
- fku
- nivå_1_4
- nivå_5
- expert
graph_relations:
- type: CONSTRAINS
  target: hourly_rate
  condition: competence_level <= 4
constraints:
- param: hourly_rate
  operator: MAX_FROM_LOOKUP
  value: framework_price_list
  condition:
    param: competence_level
    operator: IN
    value:
    - 1
    - 2
    - 3
    - 4
  action: BLOCK
  error_msg: Timpriset för nivå 1-4 får ej överstiga ramavtalets takpris för leverantören.
---

# Regel: Takpriser vid Förnyad Konkurrensutsättning
**KONTROLLERA** offererat timpris mot ramavtalets prisbilaga.

*   **Nivå 1-4:** Timpriset FÅR EJ överstiga det avtalade takpriset för aktuell roll och leverantör.
*   **Nivå 5 (Expert) / Egenformulerad roll:** Takpriserna i ramavtalet gäller EJ. Priset är fritt.