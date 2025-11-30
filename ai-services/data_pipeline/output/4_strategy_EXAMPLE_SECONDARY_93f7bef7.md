---
uuid: 93f7bef7-1154-4a13-953d-6985cd9dbc3b
doc_type: smart_block
source_file: 1-AllDocuments (17).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_4_strategy
topic_tags:
- Intervju
- Kvalitetsbedömning
- Poängsättning
- Utvärdering
entities: []
tags:
- intervju
- utvärdering
- kvalitet
- poäng
- spärrnivå
constraints:
- param: interview_score_total
  operator: MIN
  value: 5
  unit: points
  action: BLOCK
  error_msg: Anbudet måste uppnå minst 5 poäng totalt i intervjun för att inte förkastas.
---

# Exempel: Kvalitetsutvärdering via intervju
Kvalitet kan utvärderas via intervju där poäng delas ut baserat på bedömningsgrunder. Poängen kan sedan omvandlas till ett ekonomiskt mervärde (prisavdrag).
- **Poängskala:** 0-3 per bedömningsgrund.
- **Värde per poäng:** 1 poäng motsvarar 50 kr i mervärdesavdrag.
- **Spärrnivå:** Anbud med 4 poäng eller lägre totalt förkastas.