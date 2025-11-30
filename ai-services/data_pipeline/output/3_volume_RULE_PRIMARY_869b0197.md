---
uuid: 869b0197-8d84-4178-9c1f-67453f24b58f
doc_type: smart_block
source_file: Upphandlingsdokument (GDPR).pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: FINANCIALS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
- step_4_strategy
topic_tags:
- Prissättning
- Takpris
- Avropsvillkor
- Offert
entities:
- Förnyad Konkurrensutsättning
- Bilaga 01 - Priser
tags:
- takpris
- fku
- pris
- offert
- prövning
constraints:
- param: hourly_rate
  operator: MAX
  value: FROM_FRAMEWORK_AGREEMENT
  unit: sek
  action: BLOCK
  error_msg: Offererat timpris får ej överstiga gällande takpris i ramavtalet.
---

# Regel: Takpris vid Förnyad Konkurrensutsättning
**OM** avropsformen är Förnyad Konkurrensutsättning (FKU):
**DÅ** utgör de timpriser som angetts i ramavtalet (Bilaga 01) ett absolut **takpris**.

**KONTROLLERA:** Leverantören FÅR offerera ett lägre pris, men ALDRIG ett högre pris än det som är avtalat i ramavtalet.