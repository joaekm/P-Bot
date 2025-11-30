---
uuid: dc4f708d-1519-413a-a992-86d803068868
doc_type: smart_block
source_file: efterfragat-resursbehov-bilaga-b-dynamisk-rangordning---it-konsulttjanster-2021-v4.0-2022-11-21.xlsx
authority_level: PRIMARY
block_type: DEFINITION
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Geografi
- Region
- Anbudsområde
- Län
entities:
- Anbudsområde A
- Anbudsområde B
- Anbudsområde C
- Anbudsområde D
- Anbudsområde E
- Anbudsområde F
- Anbudsområde G
tags:
- regioner
- geografi
- anbudsområden
- län
constraints:
- param: location
  operator: ONE_OF
  value:
  - A
  - B
  - C
  - D
  - E
  - F
  - G
  action: BLOCK
  error_msg: Valt anbudsområde är ogiltigt. Välj mellan A-G.
---

# Definition: Geografiska Anbudsområden
Ramavtalet är indelat i sju geografiska anbudsområden (A-G):
- **A:** Norrbottens län, Västerbottens län
- **B:** Jämtlands län, Västernorrlands län
- **C:** Gävleborgs län, Dalarnas län, Värmlands län, Örebro län, Västmanlands län, Södermanlands län
- **D:** Stockholms län, Uppsala län, Gotlands län
- **E:** Västra Götalands län, Hallands län
- **F:** Östergötlands län, Jönköpings län, Kalmar län
- **G:** Skåne län, Blekinge län, Kronobergs län