Konceptbeskrivning: Arbetsstation Resurs (v2.0)

Projekt: P-Bot / Adda Upphandlingsassistent Modul: Arbetsstation Resurs (IT-konsulter) Status: Godkänd för implementation (PoC)

1. Vision & Paradigm

"Från Formulär till Intelligent Dialog" Arbetsstationen är en stateful AI-assistent som guidar användaren genom avropsprocessen. Paradigmen bygger på att systemet gör grovjobbet genom analys, och användaren verifierar resultatet.

    Aggressiv Förifyllnad: Systemet analyserar omedelbart allt indata (text/fil). Om användaren laddar upp en kravspecifikation i första steget, ska AI:n försöka fylla i alla efterföljande steg direkt, så att användarens primära interaktion blir att bekräfta ("Ja", "Ja", "Ja").

    Hybrid-Interaktion: Gränssnittet kombinerar friheten i en chatt med tydligheten i formulärkomponenter.

    Rådgivande Logik: AI:n agerar inte bara grindvakt utan strategisk rådgivare (t.ex. genom att föreslå uppdelning av affärer för snabbare leverans).

2. UX & Interaktionsdesign

Skärmen är zon-indelad för att minska kognitiv belastning och maximera överblick.

2.1 Huvudvyn (Chatt & Input)

    Sticky Header: Låst i toppen. Visar tydligt det aktiva processteget (t.ex. "Steg 2: Bedöm Kompetensnivå").

    Chatt-historik (Dialogen): Den centrala tidslinjen. Innehåller:

        AI-frågor & Analys.

        Användarsvar: Renderas som text ("Nivå 3") eller rika objekt (Tabeller/Kort).

        Systemnotiser (Färgkodad Feedback): Separerar fakta från dialog.

            🔵 Blå (Info): Pedagogiska tips (t.ex. prissnitt).

            🟢 Grön (Framsteg): Bekräftelse/Checkpoint.

            🔴 Röd/Orange (Regel): Tvingande spärrar (t.ex. "Nivå 4 kräver FKU").

    Dynamisk Input-zon (Botten): Kontextuellt arbetsområde som byter skepnad:

        Läge A (Strukturerat): Visar knappar, sliders, dropdowns för snabba val.

        Läge B (Fritext): Via en tydlig "Hjälp/Fråga"-knapp fälls ett textfält ut för komplexa frågor eller instruktioner.

2.2 Navigering (Sidopanel)

    Progress Bar: En vertikal tidslinje till höger som visar de 4 processtegen.

    Funktion: Ger överblick och markerar avklarade moment med en bock.

3. Processflödet (De 4 Stegen)

Processen leder användaren från behov till strategi.

Steg 1: Beskriv Behov

    Syfte: Identifiera "VAD" (Roll), "HUR MÅNGA" (Volym) och "VAR" (Plats).

    Interaktion: Fri text eller filuppladdning.

    AI-Logik (Agent: Role):

        Extraherar data och mappar mot Kompetensområden/Exempelroller i Bilaga A.

        Varukorgs-hantering: Identifierar om behovet innehåller flera olika roller (t.ex. "3 utvecklare och 1 projektledare") och skapar en objektlista.

Steg 2: Bedöm Kompetensnivå (Loop)

    Syfte: Fastställa senioritet (Nivå 1–5).

    Interaktion: Slider/Val per rolltyp.

    AI-Logik (Agent: Level):

        Matchar erfarenhet och ansvar mot definitionerna i Avtalskortet.

        Loop: Om varukorgen innehåller olika roller, itererar systemet detta steg för varje roll (då nivåerna skiljer sig åt).

Steg 3: Volym & Pris

    Syfte: Kvantifiera och kostnadsberäkna.

    Interaktion: Bekräfta antal, omfattning (%) och period.

    AI-Logik (Pris-lookup):

        Hämtar takpris från Prislistan baserat på Roll, Nivå och Region.

        Presenterar estimerad kostnad (Blå Systemnotis).

Steg 4: Fastställ Avropsform & Strategi

    Syfte: Bestämma metod (Dynamisk Rangordning vs FKU) och optimera affären.

    AI-Logik (Agent: Strategy):

        Regelkontroll: Nivå 4 och 5 kräver Förnyad Konkurrensutsättning (FKU). Nivå 1–3 tillåter Dynamisk Rangordning (DR).

        Optimering ("Split Deal"): Om varukorgen är blandad (t.ex. Nivå 3 + Nivå 5), erbjuder AI:n två vägar:

            Samlad affär (FKU): Enklast admin, men långsammare process.

            Uppdelad affär (DR + FKU): Snabbast leverans för DR-delen, men två processer.

4. Teknisk Arkitektur (AI-Strategi)

För att realisera detta i PoC:en används en Agent-baserad RAG-lösning.

    Backend: Python (Flask) + Google Gemini + ChromaDB.

    Orkestrering: En endpoint (/api/chat) som byter systemprompt (Persona) baserat på processteg.

        ROLE_AGENT (Källa: /data/roles/)

        LEVEL_AGENT (Källa: /data/levels/)

        STRATEGY_AGENT (Källa: /data/rules/)