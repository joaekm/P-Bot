# 📊 Simuleringsrapport v5.17 - "Story Analysis"

**Datum:** 2025-12-07  
**Antal scenarion:** 20  
**Version:** Förbättrad förmåga att hantera fastprisuppdrag och integrera säkerhetsaspekter. Testning av ny mervärdesavdragsfunktionalitet.

---

## 🎯 Övergripande Intryck

| Persona | Rundor | Övergripande känsla | Skulle använda igen? |
|---------|--------|---------------------|---------------------|
| Anna-Karin Holm (Verksamhetsutvecklare BI) | 5 | ⚠️ Blandad, frustrerad över formalia men ser potential. | ⚠️ Kanske |
| Henrik Wallin (Stadsjurist) | 2 | ❌ Förvirrad, känner sig otillräcklig och saknar vägledning. | ⚠️ Kanske (endast för att det inte finns något val) |
| Johan Eriksson (Verksamhetsutvecklare) | 2 | ⚠️ Lite skeptisk men ser en viss tidsbesparing. | ⚠️ Kanske |
| Sofia Berg (Digital strateg) | 1 | ⚠️ Frustrerad men produktiv, uppskattar detaljkoll men opersonlig. | ⚠️ Kanske |
| Anna Nilsson (Projektledare) | 1 | ✅ Positiv, imponerad av hantering av mervärdeskriterier. | ✅ Ja |
| Lisa Andersson (Utvecklingsledare) | 1 | ✅ Trygg, bra vägledning genom processen. | ✅ Ja |
| Oscar Lindén (IT-driftchef) | 1 | ❌ Stressad och irriterad, upplever processen som tidskrävande. | ⚠️ Kanske |
| Maria Lindgren (Enhetschef IT-utveckling) | 1 | ⚠️ Uppgiven, upplever processen som byråkratisk. | ⚠️ Kanske |
| Anders Lindqvist (IT-säkerhetschef) | 1 | ⚠️ Frustrerad över mervärdesavdrag, men positivt över kravrepetitionsfunktionen. | ⚠️ Kanske |
| Lena Bergström (Verksamhetsutvecklare Vårdinformation) | 1 | ⚠️ Utmattad men hoppfull, uppskattar fokus på säkerhet. | ⚠️ Kanske |
| Katarina Ek (IT-säkerhetschef) | 1 | ✅ Inledningsvis skeptisk men imponerad av automatisk FKU och kvalitetsfokus. | ✅ Ja |
| Karin Svensson (Produktägare E-klient) | 1 | ⚠️ Besviken över FKU och brist på flexibilitet. | ⚠️ Kanske |
| Magnus Ek (IT-driftchef) | 1 | ⚠️ Frustrerad över takpriser och viktning, men uppskattar rak kommunikation. | ⚠️ Kanske |
| Erik Johansson (Arkitektledare) | 1 | ❌ Irriterad över FKU och byråkrati, saknar personlig diskussion. | ⚠️ Kanske |
| Peter Holm (Systemansvarig) | 1 | ⚠️ Dubbel, Imponerad över förståelse av behov, irriterad över byråkrati. | ⚠️ Kanske |

---

## ✅ Positiva Mönster

### 1. **Fokus på Säkerhet Uppskattas**
Fokus på säkerhet, speciellt inom vård och kring patientdata, uppskattas och skapar förtroende.

- Persona: Katarina Ek (IT-säkerhetschef): *"Det känns ju tryggare att kunna granska leverantörerna ordentligt när det handlar om så här känsliga grejer."*
- Persona: Lena Bergström (Verksamhetsutvecklare Vårdinformation): *"Att den där AI:n verkligen fattade att säkerhetsprövning och PUBA var prio ett."*

### 2. **Effektiv identifiering av behov**
P-Bot identifierar snabbt och korrekt behoven hos användarna.

- Persona: Anna Nilsson (Projektledare): *"P-Bot identifierade mig och projektet direkt, det var smidigt."*
- Persona: Lisa Andersson (Utvecklingsledare): *"Den var ganska rak och tydlig, frågade direkt om vilken typ av konsult vi behövde och sånt."*

### 3. **Tydlig Struktur och Sammanfattning**
Användarna uppskattar den tydliga strukturen och sammanfattningen i slutet av processen.

- Persona: Anna Nilsson (Projektledare): *"Men jag gillade att den sammanfattade allt i slutet, det gav en bra överblick och bekräftade att jag inte hade missat något."*
- Persona: Peter Holm (Systemansvarig): *"När den sen sammanfattade allt på slutet kändes det faktiskt ganska bra. All information var tydlig och strukturerad."*

### 4. **Fokus på Kvalitet**
Förmågan att vikta kvalitet högre än pris uppskattas av de som vill ha kompetens framför lägsta pris.

- Persona: Sofia Berg (Digital strateg): *"Det var bra att jag fick välja 70/30, så att det inte bara handlade om billigast."*
- Persona: Anna Nilsson (Projektledare): *"Att faktiskt få möjlighet att vikta kvaliteten så högt, det kändes bra."*

---

## ⚠️ Kvarstående Frustrationsmönster

### 1. **Stelhet kring Fast Pris**
**Förekomst:** Anna-Karin Holm (Verksamhetsutvecklare BI)

Persona: *"Men sen kom frågan om timmar. TIMMAR! Fattar den inte? Jag sa ju fast pris! ”Hur stor uppskattad volym i konsulttimmar beräknar ni…” Blodtrycket steg direkt. Jag menar, varför frågar den om timmar om jag tydligt sagt fast pris?"*

**Åtgärd:** Förbättra P-Bots förmåga att hantera fastprisuppdrag genom att minimera frågor om timmar. Fokusera på resultat och leverans istället.

### 2. **FKU Upplevs Som Hinder**
**Förekomst:** Henrik Wallin (Stadsjurist), Karin Svensson (Produktägare E-klient), Erik Johansson (Arkitektledare), Maria Lindgren (Enhetschef IT-utveckling)

Persona: Henrik Wallin (Stadsjurist): *"Den delen om att vi måste använda FKU på grund av den höga nivån var lite av en vändpunkt. Jag hade ju hoppats att det skulle vara smidigare. Det kändes som ett hinder direkt, mer administration."*

**Åtgärd:** Förtydliga varför FKU är nödvändigt och ge vägledning genom processen. Fokusera på fördelarna (ökad trygghet, bättre kvalitet) istället för att det uppfattas som ett hinder.

### 3. **Brist på Vägledning kring Utvärderingskriterier**
**Förekomst:** Henrik Wallin (Stadsjurist)

Persona: *"Vilka kvalitetskriterier ska jag välja? Hur ska jag garantera att konsulten har rätt juridisk bakgrund och inte bara kan tekniska detaljer? Jag är rädd för att fastna i IT-snacket och missa det juridiska. Det kändes som om P-Bot förutsatte att jag var mer insatt i processen än jag är. Jag saknade någon form av vägledning, typ "här är några vanliga kriterier som funkar bra för DPO-roller"."*

**Åtgärd:** Integrera förslag på vanliga och relevanta utvärderingskriterier baserat på roll och behov.

### 4. **Mervärdesavdrag - Förvirrande**
**Förekomst:** Anders Lindqvist (IT-säkerhetschef)

Persona: *"Det som var lite frustrerande var att P-Bot envisades med att prata om den där "mervärdesavdrag"-grejen. Jag fattade inte riktigt hur det funkar, och jag fick en lång förklaring som mest gjorde mig ännu mer förvirrad."*

**Åtgärd:** Se över förklaringen kring mervärdesavdrag och förenkla den. Om möjligt, visualisera hur det fungerar i praktiken.

---

## 🎯 Rekommenderade Nästa Steg

1. **Förbättra Hantering av Fast Pris** - Minimera frågor om timmar och fokusera på resultat.
2. **Förtydliga Fördelarna med FKU** - Fokusera på ökad trygghet och bättre kvalitet.
3. **Integrera Förslag på Utvärderingskriterier** - Ge vägledning kring relevanta utvärderingskriterier.
4. **Förenkla Förklaringen av Mervärdesavdrag** - Gör det tydligare hur det fungerar.
5. **Erbjud Mer Personlig Interaktion** - Överväg att integrera möjligheten att prata med en mänsklig representant vid behov.

---

## 📝 Sammanfattning

P-Bot upplevs som effektiv och ger bra struktur, men många användare frustreras över stelhet, byråkrati (FKU) och brist på vägledning. Förbättringar inom fastpris-hantering, tydligare kommunikation kring FKU och förenkling av mervärdesavdrag kan öka användarvänligheten avsevärt.

---

*Genererad: 2025-12-07*  
*Version: v5.17*