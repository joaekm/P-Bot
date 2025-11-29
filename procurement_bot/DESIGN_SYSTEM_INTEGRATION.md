# Adda Design System Integration

## Översikt
Detta dokument beskriver hur Adda Design System har integrerats i prototypen.

## Filändelse
Designsystemfilen har döpts om från `AddaDesignSystem` till `AddaDesignSystem.jsx` eftersom det är en React-komponent.

## Design Tokens som implementerats

### Färger
- **Primärfärg (Brand Primary)**: `#005B59` (Petrol) - Används för header, länkar, och primära UI-element
- **Light Teal**: `#B9EAE9` - Används för knappbakgrunder och accentfärger
- **Accent**: `#D32F00` (Burnt Orange) - Används för CTA-knappar och varningar
- **Text**: `#2B2825` (Dark Grey) - Mjukare än svart
- **Bakgrund**: `#FBF4EA` (Warm Beige) - Varm beige istället för grått
- **Surface**: `#FFFFFF` (White) - För kort och modaler

### Typografi
- **Font Family**: `"Avenir Next", "Avenir", "Segoe UI", sans-serif`
- **Font Weights**: 400 (Regular), 500 (Medium), 600 (Bold)

### Border Radius
- **Small**: `4px`
- **Medium**: `8px`
- **Pill**: `20px` - Standard för knappar (enligt Design System)

## Implementerade ändringar

### CSS Variabler
Alla design tokens har lagts till som CSS-variabler i `PBotMain.css`:
- `--pbot-color-brand-primary`
- `--pbot-color-brand-light`
- `--pbot-color-brand-accent`
- `--pbot-color-text`
- `--pbot-color-background`
- `--pbot-color-surface`
- `--border-radius-pill`

### Uppdaterade Komponenter
1. **Header**: Använder nu Petrol (`#005B59`) istället för röd
2. **Knappar**: 
   - CTA-knappar använder Orange (`#D32F00`)
   - Ny variant `.adda-button--primary` med Light Teal bakgrund och Petrol text
   - Border radius uppdaterad till 20px (pill)
3. **Bakgrunder**: Body använder nu Warm Beige (`#FBF4EA`)
4. **Valda knappar**: Använder Light Teal bakgrund med Petrol text

### Bakåtkompatibilitet
Legacy-variabler behålls för bakåtkompatibilitet:
- `--pbot-color-primary` mappas till accent
- `--pbot-color-background-grey` behålls för befintliga komponenter

## Nästa steg

### Rekommenderade förbättringar
1. **Uppdatera alla knappar** till att använda nya design tokens
2. **Implementera Light Teal-varianten** för primära knappar där det passar
3. **Uppdatera kort/komponenter** för att använda Warm Beige bakgrund där det är lämpligt
4. **Granska alla färganvändningar** och uppdatera till Design System tokens

### Användning av Design System-komponenten
Designsystemfilen (`AddaDesignSystem.jsx`) kan användas som:
- Referens för design tokens
- Visuell guide för komponenter
- Dokumentation för utvecklare

## Noteringar
- Primärfärgen är **inte** röd, utan Petrol (`#005B59`)
- Röd/Orange (`#D32F00`) används sparsamt som accent
- Light Teal (`#B9EAE9`) används som bakgrundfärg på primärknappar för en mjukare "Adda"-look

