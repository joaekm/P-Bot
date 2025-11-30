---
uuid: bdc9b0ed-d05f-470b-b796-fd1d0b27e44a
doc_type: smart_block
source_file: 1-AllDocuments (23).pdf
authority_level: SECONDARY
block_type: EXAMPLE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: STRATEGY
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_4_strategy
topic_tags:
- Utvärderingsmodell
- Prisutvärdering
- Kvalitetsutvärdering
- FKU
- Takpris
entities:
- Förnyad Konkurrensutsättning
- Inera
tags:
- exempel
- fku
- utvärdering
- mervärde
- fiktivt_avdrag
- takpris
- intervju
constraints:
- param: hourly_rate
  operator: MAX
  value: 1300
  unit: sek
  action: BLOCK
  error_msg: Offererat timpris överskrider takpriset på 1300 SEK.
---

# Exempel: Utvärderingsmodell vid FKU med fiktivt avdrag
Detta är ett exempel på en utvärderingsmodell från en förnyad konkurrensutsättning.

**Principer:**
1.  **Kvalificering:** Endast anbud som uppfyller alla ska-krav går vidare.
2.  **Kvalitetsbedömning:** Offererad konsult intervjuas och poängsätts (0-12 poäng) baserat på definierade kriterier.
3.  **Fiktivt avdrag:** Varje kvalitetspoäng motsvarar ett fiktivt avdrag på timpriset (i detta fall 50 SEK per poäng).
4.  **Takpris:** Ett maximalt timpris är satt till 1300 SEK.
5.  **Utvärdering:** Det anbud med lägst `Utvärderingspris` vinner.

**Formel:**
`Anbudspris (timme) - (Kvalitetspoäng * 50 SEK) = Utvärderingspris`