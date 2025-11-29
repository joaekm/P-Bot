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
 * 2_uppdrag.jsx
 * Uppdragskonfiguration med sidebar höger
 */
export default function Uppdrag() {
  const sidebar = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AddaCard bgColor={tokens.colors.brand.lightTint}>
        <H2 style={{ fontSize: '16px', marginBottom: '12px', color: tokens.colors.brand.secondary }}>
          Hjälp & Tips
        </H2>
        <BodyText size="sm">
          Behöver du hjälp att definiera ditt uppdrag? Använd vår AI-assistent.
        </BodyText>
      </AddaCard>
      <AddaCard>
        <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>Process</H2>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          <li style={{ padding: '8px 0', fontWeight: 'bold', color: tokens.colors.brand.primary }}>1. Definiera uppdrag</li>
          <li style={{ padding: '8px 0', color: '#ccc' }}>2. Välj process</li>
          <li style={{ padding: '8px 0', color: '#ccc' }}>3. Skapa underlag</li>
        </ul>
      </AddaCard>
    </div>
  );

  const title = <PageTitle>Konfigurera uppdrag</PageTitle>;

  return (
    <LayoutSidebarRight title={title} sidebar={sidebar}>
      <AddaCard>
        <H2 style={{ marginBottom: '16px' }}>Beskriv ditt uppdrag</H2>
        <BodyText style={{ marginBottom: '16px' }}>
          Börja med att beskriva vad du vill upphandla.
        </BodyText>
        <textarea 
          style={{ 
            width: '100%', 
            minHeight: '120px', 
            padding: '12px', 
            borderRadius: tokens.borderRadius.md,
            border: `1px solid ${tokens.colors.neutral.border}`,
            fontFamily: tokens.typography.fontFamily
          }}
          placeholder="Exempel: Vi behöver en erfaren projektledare för vårt nya journalsystem..."
        />
        <div style={{ marginTop: '16px' }}>
          <AddaButton>Analysera behov</AddaButton>
        </div>
      </AddaCard>
    </LayoutSidebarRight>
  );
}

