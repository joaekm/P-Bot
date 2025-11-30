---
uuid: 947885e8-e2bd-4da8-969a-49722d3e64f6
doc_type: smart_block
source_file: 1-AllDocuments (15).pdf
authority_level: SECONDARY
block_type: RULE
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ARTIFACTS
scope_context: DOMAIN_KNOWLEDGE
suggested_phase:
- step_1_intake
topic_tags:
- Referenskrav
- Anbudskrav
- Verifiering
entities:
- Referensuppdrag
tags:
- referens
- tidsgräns
- bevis
constraints:
- param: reference_age_years
  operator: MAX
  value: 3
  unit: years
  action: BLOCK
  error_msg: Referensuppdraget får inte vara äldre än 3 år.
---

# Regel: Krav på Referensuppdrag
Anbudsgivaren SKA redovisa ett referensuppdrag där konsulten varit ansvarig för att utforma och realisera OAuth2-baserad åtkomsthantering. Referensuppdraget FÅR EJ vara äldre än tre (3) år från sista anbudsdag.