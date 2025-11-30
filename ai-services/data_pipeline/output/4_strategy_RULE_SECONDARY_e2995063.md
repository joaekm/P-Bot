---
uuid: e2995063-f5be-44af-85e8-5bc343228201
doc_type: smart_block
source_file: 1-AllDocuments (16).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Utvärderingsprocess
- Intervju
- Kvalitetsbedömning
- Mervärdesavdrag
entities: []
tags:
- intervju
- utvärdering
- kvalitetspoäng
- förkastas
constraints:
- param: interview_score_total
  operator: MIN
  value: 5
  unit: points
  action: BLOCK
  error_msg: Anbud som får 4 poäng eller lägre på intervjun kommer att förkastas.
---

# Regel: Utvärderingsintervju med Mervärdesavdrag
Kvalificerade konsulter kallas till intervju för att bedöma kvalitet. Poäng från intervjun omvandlas till ett prisavdrag på timpriset.

- **Poängskala:** 0-3 per bedömningsgrund.
- **Värde per poäng:** 50 SEK i mervärdesavdrag.
- **Kvalificeringsgräns:** Anbud med totalpoäng på 4 eller lägre förkastas.