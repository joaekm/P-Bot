---
uuid: 89111e97-0a0f-457a-87f5-dd7cd19ae2a4
doc_type: smart_block
source_file: 1-AllDocuments (19).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_2_level
topic_tags:
- Erfarenhetskrav
- Kompetenskrav
- Ska-krav
entities:
- ITIL
- SAFe
tags:
- erfarenhet
- ska_krav
- itil
- safe
- agil
constraints:
- param: experience_agile_coaching_years
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Kräver minst 3 års erfarenhet av agil coachning.
- param: experience_itil_years
  operator: MIN
  value: 5
  unit: years
  action: BLOCK
  error_msg: Kräver minst 5 års erfarenhet av ITIL.
- param: experience_safe_years
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av SAFe.
- param: experience_public_sector_years
  operator: MIN
  value: 2
  unit: years
  action: BLOCK
  error_msg: Kräver minst 2 års erfarenhet av arbete i offentlig verksamhet.
---

# Regel: Obligatoriska Erfarenhetskrav (Exempel)
Följande erfarenhetskrav var obligatoriska (ska-krav) för konsulten i Ineras avrop:

- **Agil coachning:** Minst 3 år
- **ITIL:** Minst 5 år
- **SAFe:** Minst 2 år
- **Offentlig verksamhet:** Minst 2 år

CV skulle bifogas för att styrka erfarenheten.