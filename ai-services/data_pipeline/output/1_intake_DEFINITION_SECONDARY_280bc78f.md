---
uuid: 280bc78f-d69d-4c4d-a741-d21b9c18eec6
doc_type: smart_block
source_file: 1-AllDocuments (21).pdf
authority_level: SECONDARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: ROLES
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
- step_2_level
topic_tags:
- Erfarenhetskrav
- Ska-krav
- Kompetensprofil
- IT-säkerhet
- eHälsa
entities:
- Säkerhetsstrateg
- Nivå 5
- IdP
- SAML2
- OAuth2.0
- OIDC
- Referensarkitekturen för Identitet och åtkomst
tags:
- ska_krav
- erfarenhet
- säkerhet
- nivå_5
- ehälsa
constraints:
- param: experience_years_idp_leadership
  operator: MIN
  value: 6
  unit: years
  action: BLOCK
  error_msg: Kräver minst 6 års erfarenhet av att leda utveckling av IdP-lösning.
- param: experience_years_team_leadership
  operator: MIN
  value: 6
  unit: years
  action: BLOCK
  error_msg: Kräver minst 6 års erfarenhet av att leda flera team.
- param: experience_years_ehealth_iam
  operator: MIN
  value: 3
  unit: years
  action: BLOCK
  error_msg: Kräver minst 3 års erfarenhet av Referensarkitekturen för Identitet och
    åtkomst (eHälsa).
---

# Definition: Ska-krav för Säkerhetsstrateg (Inera-exempel)
För rollen Säkerhetsstrateg (Nivå 5) ställdes följande obligatoriska erfarenhetskrav (ska-krav):

- **IdP-lösningar:** Minst 6 års erfarenhet av att leda utveckling.
- **Teamledning:** Minst 6 års erfarenhet av att leda flera team mot gemensamma mål.
- **eHälsa Arkitektur:** Minst 3 års erfarenhet av Referensarkitekturen för Identitet och åtkomst.
- **RIV TA:** Minst 3 års erfarenhet av RIV Tekniska anvisningar.
- **eHälsa Underskrift:** Minst 2 års erfarenhet av Referensarkitektur för elektronisk underskrift.
- **Teknologier:** Deltagit i minst ett projekt med minst två av: SAML2, OAuth2.0, OIDC.