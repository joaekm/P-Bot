import React from 'react';
import {
  tokens,
  LayoutSidebarRight,
  H2, BodyText,
  PageTitle,
  AddaCard,
  AddaButton
} from '../../design-system';

/**
 * 3_resurs_resultat.jsx
 * Resultat från resurskonfiguration med sidebar höger
 */
export default function ResursResultat() {
  const sidebar = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AddaCard bgColor={tokens.colors.brand.lightTint}>
        <H2 style={{ fontSize: '16px', marginBottom: '12px', color: tokens.colors.brand.secondary }}>
          Din varukorg
        </H2>
        <BodyText size="sm" style={{ marginBottom: '8px' }}>
          2 resurser konfigurerade
        </BodyText>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
          <li style={{ padding: '4px 0' }}>• Lösningsarkitekt (KN5)</li>
          <li style={{ padding: '4px 0' }}>• Projektledare (KN3)</li>
        </ul>
      </AddaCard>
      <AddaCard>
        <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>Nästa steg</H2>
        <BodyText size="sm">
          Granska din konfiguration och välj upphandlingsprocess.
        </BodyText>
      </AddaCard>
    </div>
  );

  const title = <PageTitle>Resultat: Resurskonfiguration</PageTitle>;

  return (
    <LayoutSidebarRight title={title} sidebar={sidebar}>
      <AddaCard>
        <H2 style={{ marginBottom: '16px' }}>Sammanfattning</H2>
        <BodyText style={{ marginBottom: '24px' }}>
          Baserat på ditt behov har vi identifierat följande resurser och nivåer.
        </BodyText>
        
        <div style={{ marginBottom: '24px' }}>
          <H2 style={{ fontSize: '18px', marginBottom: '12px' }}>Resurs 1: Lösningsarkitekt</H2>
          <BodyText>Kompetensnivå: KN5 (Expert)</BodyText>
          <BodyText>Omfattning: 800 timmar</BodyText>
          <BodyText>Region: Stockholm</BodyText>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <H2 style={{ fontSize: '18px', marginBottom: '12px' }}>Resurs 2: Projektledare</H2>
          <BodyText>Kompetensnivå: KN3 (Erfaren)</BodyText>
          <BodyText>Omfattning: 400 timmar</BodyText>
          <BodyText>Region: Stockholm</BodyText>
        </div>

        <div style={{ padding: '16px', backgroundColor: '#FFF5F5', borderRadius: tokens.borderRadius.md, marginBottom: '24px' }}>
          <BodyText style={{ fontWeight: 'bold', color: tokens.colors.brand.primary }}>
            OBS: Eftersom minst en resurs är KN5 krävs Förnyad Konkurrensutsättning (FKU).
          </BodyText>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <AddaButton variant="secondary">Redigera</AddaButton>
          <AddaButton>Fortsätt till processval</AddaButton>
        </div>
      </AddaCard>
    </LayoutSidebarRight>
  );
}

