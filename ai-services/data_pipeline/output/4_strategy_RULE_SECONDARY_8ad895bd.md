---
uuid: 8ad895bd-e05b-4c11-b29b-a2e691718539
doc_type: smart_block
source_file: 1-AllDocuments (8).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_4_strategy
topic_tags:
- Kvalitetsutvärdering
- Intervju
- Poängsättning
- Kvalificering
entities: []
tags:
- utvärdering
- kvalitet
- intervju
- regel
constraints:
- param: interview_score
  operator: MIN
  value: 5
  action: BLOCK
  error_msg: Anbud med 4 poäng eller lägre i kvalitetsutvärderingen förkastas.
---

# Regel: Minimikrav för Kvalitetspoäng
Vid kvalitetsutvärderingen (intervjun) måste anbudet uppnå minst 5 poäng totalt. Anbud som får 4 poäng eller lägre kommer att förkastas och inte gå vidare i utvärderingen.