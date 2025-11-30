---
uuid: f8f438c8-e143-48ec-b662-935fc64ffe34
doc_type: smart_block
source_file: 1-AllDocuments (12).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Utvärderingskriterier
- Kvalitetsbedömning
- Intervju
- Poängsättning
entities:
- SDK
tags:
- intervju
- kvalitet
- bedömning
- utvärdering
- poäng
constraints:
- param: interview_score_total
  operator: MIN
  value: 5
  unit: points
  action: BLOCK
  error_msg: Anbudet måste uppnå minst 5 poäng totalt i intervjun för att inte förkastas.
- param: interview_score_per_category
  operator: MIN
  value: 1
  unit: points
  action: BLOCK
  error_msg: Anbudet måste uppnå minst 1 poäng i varje enskild bedömningsgrund.
---

# Definition: Kvalitetskriterier vid Intervju
Kvalitet utvärderas via intervju med poäng 0-3 inom fyra områden:
1.  Kommunikativ förmåga
2.  Kompetens och förståelse för uppdraget
3.  Kompetens om tjänsten SDK
4.  Kompetens kring införandestöd

**Poäng till Avdrag:** Varje poäng (1-3) motsvarar 50 kr i mervärdesavdrag. Max 12 poäng (600 kr).
**Spärregel:** Anbud förkastas om totalpoängen är 4 eller lägre, ELLER om konsulten får 0 poäng i något enskilt område.