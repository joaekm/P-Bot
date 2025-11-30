---
uuid: 606e90ac-63f0-49d9-a6bb-4c2e76187f76
doc_type: smart_block
source_file: kontraktsvillkor-dynamisk-rangordning---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: DEFINITION
taxonomy_root: PROCESS
taxonomy_branch: PHASES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_3_volume
topic_tags:
- Leveranskontroll
- Godkännande
- Tidsfrist
entities:
- Leveranskontrollperiod
tags:
- leverans
- kontroll
- godkännande
- tidsfrist
constraints:
- param: delivery_control_period
  operator: EQUALS
  value: 30
  unit: days
  action: INFO
  error_msg: Standardperiod för leveranskontroll är 30 dagar före leveransdag.
- param: result_availability_before_control
  operator: MIN
  value: 5
  unit: workdays
  action: BLOCK
  error_msg: Resultatet måste finnas tillgängligt för kontroll senast 5 arbetsdagar
    innan leveranskontrollperioden startar.
---

# Definition: Leveranskontrollperiod
En period för att testa och godkänna uppdragsresultatet. 
- **Standardlängd:** De 30 kalenderdagarna som föregår avtalad leveransdag.
- **Krav på leverantör:** Resultatet SKA vara tillgängligt för kontroll senast fem arbetsdagar innan perioden inleds.
- **Godkännande:** Leverans anses fullgjord först när myndigheten skriftligen godkänt resultatet.