---
uuid: a9da46c9-035b-4d50-b1f4-2eca92d6d3c7
doc_type: smart_block
source_file: 1-AllDocuments (20).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_4_strategy
topic_tags:
- Kvalitetsutvärdering
- Intervju
- Mervärde
- Poängsättning
entities:
- Teams
tags:
- exempel
- intervju
- utvärdering
- kvalitet
- fku
constraints:
- param: interview_score_per_category
  operator: MIN
  value: 1
  unit: points
  action: BLOCK
  error_msg: Anbudet måste uppnå minst 1 poäng i varje bedömningsgrund under intervjun.
---

# Exempel: Kvalitetsutvärdering via Intervju (Inera)
Kvalitet utvärderas via en intervju där konsulten poängsätts (0-3) på tre bedömningsgrunder. Maximalt mervärdesavdrag är 900 kr (100 kr per poäng). Ett anbud måste få minst en (1) poäng per bedömningsgrund för att inte förkastas.