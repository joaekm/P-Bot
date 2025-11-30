---
uuid: 6c036d6a-3c2d-4918-986e-ec5a228ce0aa
doc_type: smart_block
source_file: 1-AllDocuments (19).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Avtalstid
- Förlängningsoption
- Uppskattat värde
- Uppdragsvolym
entities:
- Inera AB
tags:
- avtalstid
- option
- budget
- volym
- år_2024
constraints:
- param: contract_length_months
  operator: MAX
  value: 21
  unit: months
  action: BLOCK
  error_msg: Total avtalstid inklusive optioner får ej överstiga 21 månader för detta
    uppdrag.
---

# Definition: Avtalstid och Omfattning (Exempel)
Avropskontraktet för Ineras Transformationsledare hade följande ramar:

- **Kontraktstid:** 2024-01-02 till 2024-09-30 (~9 månader).
- **Option:** Ensidig rätt för beställaren att förlänga med upp till 12 månader.
- **Total maxlängd:** ca 21 månader.
- **Uppskattat värde:** 3 900 000 SEK (ej ett garanterat värde).
- **Omfattning:** Cirka 100% av en heltidsekvivalent.