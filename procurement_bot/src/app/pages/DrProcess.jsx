import React from 'react';
import {
  tokens,
  LayoutSidebarLeft,
  H2, BodyText,
  PageTitle,
  AddaCard,
  AddaButton
} from '../../design-system';

/**
 * 4_dr_process.jsx
 * Direktavrop-processöversikt med sidebar vänster
 */
export default function DRProcess() {
  const sidebar = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AddaCard bgColor={tokens.colors.brand.lightTint}>
        <H2 style={{ fontSize: '16px', marginBottom: '12px', color: tokens.colors.brand.secondary }}>
          DR-Process
        </H2>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
          <li style={{ padding: '8px 0', fontWeight: 'bold', color: tokens.colors.brand.primary }}>→ 1. Behovsdefinition</li>
          <li style={{ padding: '8px 0' }}>2. Leverantörsval</li>
          <li style={{ padding: '8px 0' }}>3. Avrop</li>
        </ul>
      </AddaCard>
      <AddaCard>
        <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>Snabbfakta</H2>
        <BodyText size="sm">Direktavrop är den enklaste formen av avrop från ramavtal.</BodyText>
      </AddaCard>
    </div>
  );

  const title = <PageTitle>Direktavrop (DR)</PageTitle>;

  return (
    <LayoutSidebarLeft title={title} sidebar={sidebar}>
      <AddaCard style={{ marginBottom: '24px' }}>
        <H2 style={{ marginBottom: '16px' }}>Steg 1: Behovsdefinition</H2>
        <BodyText style={{ marginBottom: '24px' }}>
          Ditt behov kan hanteras via Direktavrop (DR). Detta är den enklaste och snabbaste processen 
          eftersom dina resurser ligger inom KN2-KN4 och leverantörerna redan har avtalade priser.
        </BodyText>

        <H2 style={{ fontSize: '18px', marginBottom: '12px' }}>Hur fungerar Direktavrop?</H2>
        <ol style={{ marginLeft: '20px', marginBottom: '24px' }}>
          <li><BodyText>Du definierar ditt behov (klart! ✓)</BodyText></li>
          <li><BodyText>Systemet rekommenderar lämpliga leverantörer baserat på pris och tidigare prestanda</BodyText></li>
          <li><BodyText>Du väljer leverantör och skickar en beställning</BodyText></li>
        </ol>

        <div style={{ padding: '16px', backgroundColor: '#F0FFF4', borderRadius: tokens.borderRadius.md, marginBottom: '24px', border: '1px solid #38A169' }}>
          <BodyText style={{ fontWeight: 'bold', marginBottom: '8px', color: '#2F855A' }}>Fördelar med DR</BodyText>
          <ul style={{ marginLeft: '20px', fontSize: '14px' }}>
            <li>Snabbast process (kan vara klart på dagar)</li>
            <li>Minimal administration</li>
            <li>Förhandlade priser</li>
          </ul>
        </div>

        <AddaButton>Fortsätt till leverantörsval</AddaButton>
      </AddaCard>

      <AddaCard bgColor={tokens.colors.neutral.bg}>
        <H2 style={{ marginBottom: '12px' }}>Ditt behov</H2>
        <BodyText size="sm" style={{ marginBottom: '8px' }}><strong>Roll:</strong> Projektledare</BodyText>
        <BodyText size="sm" style={{ marginBottom: '8px' }}><strong>Nivå:</strong> KN3 (Erfaren)</BodyText>
        <BodyText size="sm" style={{ marginBottom: '8px' }}><strong>Omfattning:</strong> 400 timmar</BodyText>
        <BodyText size="sm"><strong>Region:</strong> Stockholm</BodyText>
      </AddaCard>
    </LayoutSidebarLeft>
  );
}

