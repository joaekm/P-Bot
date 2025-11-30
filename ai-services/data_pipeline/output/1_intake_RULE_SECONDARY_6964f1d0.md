---
uuid: 6964f1d0-2d09-4dee-b139-c180885f7728
doc_type: smart_block
source_file: 1-AllDocuments (12).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ARTIFACTS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Referenskrav
- Erfarenhetskrav
- Validering
entities:
- Referensuppdrag
- Bilaga 1
tags:
- referens
- krav
- validering
- införandestöd
constraints:
- param: reference_count
  operator: EQUALS
  value: 2
  unit: references
  action: BLOCK
  error_msg: Exakt två referensuppdrag måste lämnas.
- param: reference_age_years
  operator: MAX
  value: 3
  unit: years
  action: BLOCK
  error_msg: Referensuppdrag får vara maximalt 3 år gamla.
---

# Regel: Krav på referensuppdrag
**KRAV:** Ansvarig projektledare ska inkomma med två (2) referensuppdrag.
- **Ålder:** Referenserna får inte vara äldre än tre (3) år från sista anbudsdag.
- **Innehåll 1:** Ett uppdrag ska påvisa erfarenhet av att utveckla metodik för införandestöd.
- **Innehåll 2:** Ett uppdrag ska avse ledning av införandestöd av digitala tjänster för regioner/kommuner.