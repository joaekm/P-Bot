---
uuid: cd5c24be-d884-4bae-a46c-251c92a0c6ea
doc_type: smart_block
source_file: 1-AllDocuments (15).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_4_strategy
topic_tags:
- Utvärderingskriterier
- Kvalitetsbedömning
- Intervju
- Minsta poängkrav
entities: []
tags:
- utvärdering
- intervju
- kvalitet
- poängsättning
constraints:
- param: interview_score_total
  operator: GT
  value: 4
  unit: points
  action: BLOCK
  error_msg: Anbudet förkastas. Total intervjupoäng understiger minimikravet (måste
    vara > 4).
---

# Regel: Minimikrav för Intervjupoäng
Utvärdering sker via intervju där poäng (0-3) ges inom fyra bedömningsgrunder. Anbud som erhåller en sammantagen poäng på fyra (4) eller lägre kommer att förkastas och inte gå vidare i utvärderingen.