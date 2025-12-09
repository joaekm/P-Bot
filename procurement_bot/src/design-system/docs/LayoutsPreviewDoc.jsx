import React from 'react';
import { tokens } from '../tokens';
import { LayoutLanding, LayoutSidebarRight } from '../layouts';
import { AddaCard } from '../components/AddaCard';
import { AddaButton } from '../components/AddaButton';
import { H1, H2, H3, BodyText } from '../components/AddaTypography';
import { ListItem } from '../list/ListItem';
import ChatWindow from '../chat/ChatWindow';
import { AIAnswerContainer } from '../chat/AIAnswerContainer';
import { UserAnswerContainer } from '../chat/UserAnswerContainer';
import ActionPanel from '../chat/ActionPanel';
import ProcessProgressBar from '../components/ProcessProgressBar';
import { Calendar, Users, FileText } from 'lucide-react';

/**
 * LayoutsPreviewDoc
 * Documentation page showing available layout components with realistic examples
 * based on the actual application pages (Dashboard & ResursWorkstation).
 */
const LayoutsPreviewDoc = () => {
  
  // --- Dashboard Example Content ---
  // Hero-innehållet - bara rubrik, text och knappar (LayoutLanding hanterar bakgrundsfärg och textfärg)
  const dashboardHero = (
    <>
      <H1 style={{ marginBottom: '24px', fontSize: '28px', color: 'inherit' }}>
        Välkommen till Adda stödverktyg
      </H1>
      <BodyText size="lg" style={{ marginBottom: '32px', lineHeight: '1.6', color: 'inherit' }}>
        Ramavtalet erbjuder ett brett och kvalitativt utbud av IT-och verksamhetsutvecklingskonsulter.
      </BodyText>
      <BodyText size="lg" style={{ marginBottom: '24px', fontWeight: 'bold', color: 'inherit' }}>
        Välj vad du vill upphandla:
      </BodyText>
      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <AddaButton variant="secondary">Resurser/Konsulter</AddaButton>
        <AddaButton variant="secondary">Uppdrag/Projekt</AddaButton>
      </div>
    </>
  );

  const dashboardContent = (
    <div style={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: `${tokens.spacing['6xl']} ${tokens.spacing['4xl']}` 
    }}>
      <section style={{ marginBottom: tokens.spacing['6xl'] }}>
        <H2 style={{ marginBottom: tokens.spacing['4xl'], color: tokens.colors.neutral.text }}>
          Pågående avrop
        </H2>
        <ListItem
          backgroundColor={tokens.colors.neutral.surface}
          badge="Aktivt"
          badgeColor="green"
          title="IT-konsulter för digitaliseringsprojekt"
          description="Avrop av systemutvecklare och lösningsarkitekter för pågående digitalisering..."
          metadata={[
            { icon: <Calendar size={16} />, text: 'Start: 15 nov 2024' },
            { icon: <Users size={16} />, text: '3 konsulter' }
          ]}
          actionButton={<AddaButton size="small">Hantera</AddaButton>}
        />
      </section>
      <section>
        <H2 style={{ marginBottom: tokens.spacing['4xl'], color: tokens.colors.neutral.text }}>
          Avslutade avrop
        </H2>
        <ListItem
            backgroundColor={tokens.colors.neutral.surface}
            badge="Avslutat"
            badgeColor="blue"
            title="Projektledare för förvaltningsprojekt"
            description="Upphandling av certifierad projektledare för ledning av förvaltningsprojekt..."
            metadata={[
              { icon: <Calendar size={16} />, text: 'Slut: 30 sep 2024' },
              { icon: <Users size={16} />, text: '1 konsult' }
            ]}
            actionButton={<AddaButton size="small" variant="secondary">Detaljer</AddaButton>}
          />
      </section>
    </div>
  );

  // --- Workstation Example Content ---
  const processSteps = [
    { id: 1, title: 'Beskriv Behov' },
    { id: 2, title: 'Bedöm Kompetensnivå' },
    { id: 3, title: 'Volym & Pris' },
    { id: 4, title: 'Avropsform & Strategi' }
  ];

  const workstationSidebar = (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <AddaCard style={{ padding: tokens.spacing['2xl'] }}>
        <ProcessProgressBar 
          steps={processSteps} 
          currentStepIndex={0}
        />
      </AddaCard>
      
      <AddaCard bgColor="#FFF" style={{ padding: tokens.spacing['2xl'] }}>
        <BodyText size="sm" bold>Information</BodyText>
        <BodyText size="xs" style={{ fontWeight: 'bold', marginBottom: '8px' }}>
          Så här behandlar vi din information och uppladdade filer.
        </BodyText>
        <BodyText size="xs">
          Kom ihåg att AI ibland kan lämna fel information och att du som avropande part alltid är skyldig att lämna rätt uppgifter och är ansvarig för inlämnade underlag.
        </BodyText>
      </AddaCard>
    </div>
  );

  const workstationChat = (
    <ChatWindow
      currentStepNumber={1}
      currentStepTitle="Beskriv Behov"
      minHeight="500px"
      maxHeight="600px" // Fixed height for documentation display
      style={{ height: '600px' }}
      inputZone={
        <ActionPanel
          mode="text_input"
          placeholder="Beskriv ditt behov..."
          actions={[]}
          onTextSubmit={() => {}}
        />
      }
    >
      <AIAnswerContainer text="Hej! Jag är din AI-assistent för resursupphandling. Vad behöver du hjälp med idag?" />
      <UserAnswerContainer text="Jag behöver en projektledare för ett nytt IT-projekt." />
      <AIAnswerContainer text="Uppfattat. Vilken kompetensnivå tänker du dig? (Nivå 1-5)" />
    </ChatWindow>
  );

  return (
    <div>
      <H1 style={{ marginBottom: tokens.spacing['2xl'] }}>Sid-layouter</H1>
      <BodyText style={{ marginBottom: tokens.spacing['4xl'] }}>
        Färdiga layoutmallar baserade på applikationens huvudvyer: <strong>Dashboard</strong> och <strong>Workstation</strong>.
      </BodyText>

      {/* LayoutLanding (Dashboard) */}
      <section style={{ marginBottom: tokens.spacing['6xl'] }}>
        <H2>LayoutLanding</H2>
        <BodyText>Landningssida med hero-sektion och fullbredd innehåll. Motsvarar startsidan (Dashboard).</BodyText>
        
        <div style={{ 
          border: `1px solid ${tokens.colors.neutral.border}`, 
          borderRadius: tokens.borderRadius.lg, 
          overflow: 'hidden', 
          marginTop: tokens.spacing.lg,
          height: '600px', // Fixed height container with scroll for preview
          overflowY: 'auto'
        }}>
          <LayoutLanding hero={dashboardHero}>
            {dashboardContent}
          </LayoutLanding>
        </div>
      </section>

      {/* LayoutSidebarRight (Workstation) */}
      <section style={{ marginBottom: tokens.spacing['6xl'] }}>
        <H2>LayoutSidebarRight</H2>
        <BodyText>Layout med sidofält till höger. Motsvarar arbetsvyn (ResursWorkstation).</BodyText>
        
        <div style={{ 
          border: `1px solid ${tokens.colors.neutral.border}`, 
          borderRadius: tokens.borderRadius.lg, 
          overflow: 'hidden', 
          marginTop: tokens.spacing.lg,
          // Workstation layout fills height, so we give the container a fixed height
          height: '700px',
          display: 'flex', 
          flexDirection: 'column'
        }}>
          {/* Note: In real app, LayoutSidebarRight often takes full viewport height. 
              Here we contain it within the preview div. */}
          <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
             <LayoutSidebarRight sidebar={workstationSidebar}>
                <div style={{ padding: '24px', height: '100%', boxSizing: 'border-box' }}>
                  {workstationChat}
                </div>
             </LayoutSidebarRight>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LayoutsPreviewDoc;
