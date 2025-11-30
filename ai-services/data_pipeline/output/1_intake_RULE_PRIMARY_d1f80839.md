---
uuid: d1f80839-f2aa-4458-81c5-83a9091658f2
doc_type: smart_block
source_file: kontraktsvillkor-dynamisk-rangordning---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: RULE
taxonomy_root: BUSINESS_CONCEPTS
taxonomy_branch: GOVERNANCE
scope_context: GENERAL_LEGAL
suggested_phase:
- step_1_intake
topic_tags:
- GDPR
- Personuppgiftsbehandling
- Tredjelandsöverföring
- Dataskydd
entities:
- GDPR
- EU
- EES
- Integritetsskyddsmyndigheten
tags:
- gdpr
- dataskydd
- tredjeland
- personuppgifter
- standardvillkor
constraints:
- param: data_transfer_policy
  operator: ONE_OF
  value:
  - option_1_allowed_with_safeguards
  - option_2_requires_pre_approval
  - option_3_forbidden
  action: WARN
  error_msg: Ett val för dataöverföring till tredjeland måste anges. Om inget anges
    gäller alternativ 2 som standard.
---

# Regel: Överföring av personuppgifter till tredje land (GDPR)
Vid avrop SKA den upphandlande myndigheten ange en av tre policys för dataöverföring utanför EU/EES:
- **Alternativ 1:** Tillåtet med tillräckliga garantier (t.ex. standardavtalsklausuler).
- **Alternativ 2:** Tillåtet endast efter skriftligt förhandsgodkännande från myndigheten för varje enskild överföring.
- **Alternativ 3:** Strikt förbjudet.

**STANDARDREGEL:** Om inget alternativ anges, gäller automatiskt alternativ **2**.