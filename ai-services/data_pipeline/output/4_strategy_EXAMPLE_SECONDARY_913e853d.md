---
uuid: 913e853d-d127-4c5d-a244-30963b62d13d
doc_type: smart_block
source_file: 1-AllDocuments (6).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Kvalitetsutvärdering
- Intervju
- Poängsättning
- Kvalificeringskrav
entities: []
tags:
- exempel
- intervju
- utvärdering
- kvalitet
- förkasta
constraints:
- param: interview_score_total
  operator: MIN
  value: 5
  unit: points
  action: BLOCK
  error_msg: Anbudet förkastas om total poäng från intervju är 4 eller lägre.
---

# Exempel: Kvalitetsutvärdering via Intervju
För att bedöma kvalitet kan en intervju användas. I detta exempel poängsätts konsulten (0-3p) inom fyra bedömningsgrunder. Varje poäng motsvarar ett prisavdrag (50 kr).

**Regel:** Anbud som får 4 poäng eller lägre sammantaget kommer att förkastas.