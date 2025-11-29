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
 * 5_fku_ws.jsx
 * FKU Arbetsstation med sidebar höger
 */
export default function FKUWorkstation() {
  const sidebar = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AddaCard bgColor={tokens.colors.brand.lightTint}>
        <H2 style={{ fontSize: '16px', marginBottom: '12px', color: tokens.colors.brand.secondary }}>
          Status
        </H2>
        <BodyText size="sm" style={{ marginBottom: '8px' }}>
          <strong>Steg:</strong> Kravspecifikation
        </BodyText>
        <BodyText size="sm">
          <strong>Framsteg:</strong> 60%
        </BodyText>
      </AddaCard>
      <AddaCard>
        <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>Checkpunkter</H2>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
          <li style={{ padding: '4px 0' }}>✓ Behov definierat</li>
          <li style={{ padding: '4px 0' }}>✓ Roller identifierade</li>
          <li style={{ padding: '4px 0', fontWeight: 'bold' }}>→ Kravspec under arbete</li>
          <li style={{ padding: '4px 0', color: '#ccc' }}>Utvärderingskriterier</li>
          <li style={{ padding: '4px 0', color: '#ccc' }}>Anbudsinfordran</li>
        </ul>
      </AddaCard>
    </div>
  );

  const title = <PageTitle>FKU Arbetsstation</PageTitle>;

  return (
    <LayoutSidebarRight title={title} sidebar={sidebar}>
      <AddaCard style={{ marginBottom: '24px' }}>
        <H2 style={{ marginBottom: '16px' }}>Granska kravspecifikation</H2>
        <BodyText style={{ marginBottom: '16px' }}>
          Vi har genererat ett utkast baserat på din input. Granska och justera efter behov.
        </BodyText>

        <div style={{ 
          padding: '16px', 
          backgroundColor: tokens.colors.neutral.bg, 
          borderRadius: tokens.borderRadius.md,
          border: `1px solid ${tokens.colors.neutral.border}`,
          marginBottom: '16px'
        }}>
          <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>1. Uppdragsbeskrivning</H2>
          <BodyText size="sm" style={{ marginBottom: '16px' }}>
            Vi söker en Lösningsarkitekt (KN5) och en Projektledare (KN3) för att utveckla och implementera 
            ett nytt journalsystem. Uppdraget omfattar analys, design, implementation och dokumentation.
          </BodyText>

          <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>2. Kompetensprofiler</H2>
          <BodyText size="sm" style={{ fontWeight: 'bold' }}>Lösningsarkitekt (KN5)</BodyText>
          <ul style={{ marginLeft: '20px', fontSize: '14px', marginBottom: '12px' }}>
            <li>Minst 13 års erfarenhet av systemarkitektur</li>
            <li>Expertis inom integration och API-design</li>
            <li>Erfarenhet av vårdsystemlösningar</li>
          </ul>

          <BodyText size="sm" style={{ fontWeight: 'bold' }}>Projektledare (KN3)</BodyText>
          <ul style={{ marginLeft: '20px', fontSize: '14px' }}>
            <li>6-9 års erfarenhet av IT-projektledning</li>
            <li>Certifiering inom projektmetodik (PMP/PRINCE2)</li>
            <li>Erfarenhet av offentlig sektor</li>
          </ul>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <AddaButton>Redigera</AddaButton>
          <AddaButton variant="secondary">Godkänn & fortsätt</AddaButton>
        </div>
      </AddaCard>

      <AddaCard>
        <H2 style={{ marginBottom: '12px' }}>AI-Assistent</H2>
        <BodyText size="sm" style={{ marginBottom: '12px' }}>
          Behöver du hjälp att förbättra kravspecifikationen?
        </BodyText>
        <textarea 
          style={{ 
            width: '100%', 
            minHeight: '80px', 
            padding: '12px', 
            borderRadius: tokens.borderRadius.md,
            border: `1px solid ${tokens.colors.neutral.border}`,
            fontFamily: tokens.typography.fontFamily,
            fontSize: '14px'
          }}
          placeholder="Ställ en fråga eller be om förslag..."
        />
        <div style={{ marginTop: '12px' }}>
          <AddaButton size="small">Skicka</AddaButton>
        </div>
      </AddaCard>
    </LayoutSidebarRight>
  );
}

