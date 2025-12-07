---
uuid: geo-resolution-001
doc_type: smart_block
source_file: avropsvagledning---it-konsulttjanster-2021.pdf
authority_level: PRIMARY
block_type: DATA_POINTER
taxonomy_root: DOMAIN_OBJECTS
taxonomy_branch: LOCATIONS
scope_context: FRAMEWORK_SPECIFIC
suggested_phase:
- step_1_intake
topic_tags:
- Geografi
- Anbudsområde
- Region
- Län
- Plats
- Kommun
- Stad
entities: []
---

# Geografisk mappning: Län → Anbudsområde

När användaren anger en plats (stad, kommun eller län), använd denna mappning för att identifiera korrekt anbudsområde.

## Anbudsområden

| Anbudsområde | Namn | Ingående län |
|--------------|------|--------------|
| A | Norra Norrland | Norrbotten, Västerbotten |
| B | Mellersta Norrland | Jämtland, Västernorrland |
| C | Norra Mellansverige | Gävleborg, Dalarna, Värmland, Örebro, Västmanland, Södermanland |
| D | Stockholm | Stockholm, Uppsala, Gotland |
| E | Västsverige | Västra Götaland, Halland |
| F | Småland/Östergötland | Östergötland, Jönköping, Kalmar |
| G | Sydsverige | Skåne, Blekinge, Kronoberg |

## Komplett Län → Anbudsområde mappning

| Län | Anbudsområde | Områdesnamn |
|-----|--------------|-------------|
| Norrbotten | A | Norra Norrland |
| Västerbotten | A | Norra Norrland |
| Jämtland | B | Mellersta Norrland |
| Västernorrland | B | Mellersta Norrland |
| Gävleborg | C | Norra Mellansverige |
| Dalarna | C | Norra Mellansverige |
| Värmland | C | Norra Mellansverige |
| Örebro | C | Norra Mellansverige |
| Västmanland | C | Norra Mellansverige |
| Södermanland | C | Norra Mellansverige |
| Stockholm | D | Stockholm |
| Uppsala | D | Stockholm |
| Gotland | D | Stockholm |
| Västra Götaland | E | Västsverige |
| Halland | E | Västsverige |
| Östergötland | F | Småland/Östergötland |
| Jönköping | F | Småland/Östergötland |
| Kalmar | F | Småland/Östergötland |
| Skåne | G | Sydsverige |
| Blekinge | G | Sydsverige |
| Kronoberg | G | Sydsverige |

## Residensstäder (länshuvudorter)

| Stad | Län | Anbudsområde |
|------|-----|--------------|
| Luleå | Norrbotten | A |
| Umeå | Västerbotten | A |
| Östersund | Jämtland | B |
| Härnösand | Västernorrland | B |
| Gävle | Gävleborg | C |
| Falun | Dalarna | C |
| Karlstad | Värmland | C |
| Örebro | Örebro | C |
| Västerås | Västmanland | C |
| Nyköping | Södermanland | C |
| Stockholm | Stockholm | D |
| Uppsala | Uppsala | D |
| Visby | Gotland | D |
| Gotland | Gotland | D |
| Göteborg | Västra Götaland | E |
| Halmstad | Halland | E |
| Linköping | Östergötland | F |
| Jönköping | Jönköping | F |
| Kalmar | Kalmar | F |
| Malmö | Skåne | G |
| Karlskrona | Blekinge | G |
| Växjö | Kronoberg | G |

**OBS:** Visby är residensstad på Gotland. Kommunen heter "Gotland" (ej "Visby kommun").

## Instruktion för svar

När användaren anger en plats, bekräfta med formatet:

> "Noterat. [Stad] (Anbudsområde [X] – [Områdesnamn])"

**Exempel:**
- Input: "Härnösand" → "Noterat. Härnösand (Anbudsområde B – Mellersta Norrland)"
- Input: "Stockholm" → "Noterat. Stockholm (Anbudsområde D – Stockholm)"
- Input: "Göteborg" → "Noterat. Göteborg (Anbudsområde E – Västsverige)"
- Input: "Linköping" → "Noterat. Linköping (Anbudsområde F – Småland/Östergötland)"
- Input: "Luleå" → "Noterat. Luleå (Anbudsområde A – Norra Norrland)"

## Källa

Avropsvägledningen IT-konsulttjänster 2021, Kapitel 2 "Omfattning"

