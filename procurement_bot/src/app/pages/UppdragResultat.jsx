import React from 'react';
import {
  tokens,
  LayoutFullWidth,
  H2, BodyText,
  PageTitle,
  AddaCard,
  AddaButton
} from '../../design-system';

/**
 * 3_uppdrag_resultat.jsx
 * Resultat från uppdragskonfiguration med fullbredd
 */
export default function UppdragResultat() {
  return (
    <LayoutFullWidth>
      <PageTitle>Resultat: Uppdragskonfiguration</PageTitle>
      
      <AddaCard style={{ marginBottom: '24px' }}>
        <H2 style={{ marginBottom: '16px' }}>AI-Analys av ditt behov</H2>
        <BodyText style={{ marginBottom: '16px' }}>
          Baserat på din beskrivning har vi identifierat följande:
        </BodyText>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div style={{ padding: '16px', backgroundColor: tokens.colors.neutral.bg, borderRadius: tokens.borderRadius.md }}>
            <BodyText style={{ fontWeight: 'bold', marginBottom: '8px' }}>Typ av uppdrag</BodyText>
            <BodyText>IT-utveckling & Implementation</BodyText>
          </div>
          <div style={{ padding: '16px', backgroundColor: tokens.colors.neutral.bg, borderRadius: tokens.borderRadius.md }}>
            <BodyText style={{ fontWeight: 'bold', marginBottom: '8px' }}>Komplexitet</BodyText>
            <BodyText>Hög (Expertkompetens krävs)</BodyText>
          </div>
          <div style={{ padding: '16px', backgroundColor: tokens.colors.neutral.bg, borderRadius: tokens.borderRadius.md }}>
            <BodyText style={{ fontWeight: 'bold', marginBottom: '8px' }}>Uppskattad omfattning</BodyText>
            <BodyText>1200 timmar</BodyText>
          </div>
        </div>

        <H2 style={{ fontSize: '18px', marginBottom: '12px' }}>Rekommenderade roller</H2>
        <ul style={{ marginLeft: '20px', marginBottom: '24px' }}>
          <li><BodyText>Lösningsarkitekt (KN5) - 800 timmar</BodyText></li>
          <li><BodyText>Projektledare (KN3) - 400 timmar</BodyText></li>
        </ul>

        <div style={{ display: 'flex', gap: '12px' }}>
          <AddaButton variant="secondary">Justera</AddaButton>
          <AddaButton>Acceptera & fortsätt</AddaButton>
        </div>
      </AddaCard>

      <AddaCard bgColor={tokens.colors.brand.bgHero}>
        <H2 style={{ marginBottom: '12px', color: tokens.colors.brand.primary }}>Nästa steg</H2>
        <BodyText>
          Efter att du accepterat rekommendationerna guidar vi dig till rätt upphandlingsprocess baserat på ditt behov.
        </BodyText>
      </AddaCard>
    </LayoutFullWidth>
  );
}

