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
 * 4_fku_process.jsx
 * FKU-processöversikt med sidebar vänster
 */
export default function FKUProcess() {
  const sidebar = (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <AddaCard bgColor={tokens.colors.brand.lightTint}>
        <H2 style={{ fontSize: '16px', marginBottom: '12px', color: tokens.colors.brand.secondary }}>
          FKU-Process
        </H2>
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '14px' }}>
          <li style={{ padding: '8px 0', fontWeight: 'bold', color: tokens.colors.brand.primary }}>→ 1. Förberedelse</li>
          <li style={{ padding: '8px 0' }}>2. Kravspecifikation</li>
          <li style={{ padding: '8px 0' }}>3. Anbudsinfordran</li>
          <li style={{ padding: '8px 0' }}>4. Utvärdering</li>
          <li style={{ padding: '8px 0' }}>5. Tilldelning</li>
        </ul>
      </AddaCard>
      <AddaCard>
        <H2 style={{ fontSize: '16px', marginBottom: '12px' }}>Dokument</H2>
        <BodyText size="sm">0 dokument uppladdade</BodyText>
      </AddaCard>
    </div>
  );

  const title = <PageTitle>Förnyad Konkurrensutsättning (FKU)</PageTitle>;

  return (
    <LayoutSidebarLeft title={title} sidebar={sidebar}>
      <AddaCard style={{ marginBottom: '24px' }}>
        <H2 style={{ marginBottom: '16px' }}>Steg 1: Förberedelse</H2>
        <BodyText style={{ marginBottom: '24px' }}>
          Eftersom ditt behov inkluderar en KN5-resurs (Expert), måste upphandlingen genomföras via Förnyad Konkurrensutsättning (FKU). 
          Detta innebär att du behöver skapa ett komplett upphandlingsunderlag och bjuda in leverantörer att lämna anbud.
        </BodyText>

        <H2 style={{ fontSize: '18px', marginBottom: '12px' }}>Vad behöver du förbereda?</H2>
        <ul style={{ marginLeft: '20px', marginBottom: '24px' }}>
          <li><BodyText>Kravspecifikation (beskrivning av uppdraget)</BodyText></li>
          <li><BodyText>Kompetensprofiler för efterfrågade roller</BodyText></li>
          <li><BodyText>Utvärderingskriterier och viktning</BodyText></li>
          <li><BodyText>Tidsplan för upphandlingen</BodyText></li>
        </ul>

        <div style={{ padding: '16px', backgroundColor: tokens.colors.ui.cardBgBlue, borderRadius: tokens.borderRadius.md, marginBottom: '24px' }}>
          <BodyText style={{ fontWeight: 'bold', marginBottom: '8px' }}>Tips från Lotsen</BodyText>
          <BodyText size="sm">
            Vi kan hjälpa dig att generera ett utkast till kravspecifikation baserat på den information du redan har delat. 
            Vill du att vi gör det?
          </BodyText>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <AddaButton>Generera utkast</AddaButton>
          <AddaButton variant="secondary">Ladda upp befintligt dokument</AddaButton>
        </div>
      </AddaCard>
    </LayoutSidebarLeft>
  );
}

