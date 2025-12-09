import React from 'react';
import {
  LayoutLanding,
  H1, H2, BodyText,
  AddaCard,
  AddaButton,
  ListItem,
  tokens
} from '../../design-system';
import { Calendar, Users, FileText } from 'lucide-react';

/**
 * 1_dashboard.jsx
 * Landningssida med översikt
 */
export default function Dashboard({ onNavigate }) {
  const heroContent = (
    <>
      <H1 style={{ marginBottom: '24px', fontSize: '28px', color: 'inherit' }}>
        Välkommen till Adda stödverktyg för IT-konsulttjänster 2021
      </H1>
      <BodyText size="lg" style={{ marginBottom: '32px', lineHeight: '1.6', color: 'inherit' }}>
        Ramavtalet erbjuder ett brett och kvalitativt utbud av IT-och verksamhetsutvecklingskonsulter. Det ska fungera som ett stöd i er digitaliseringsresa och hjälpa er att uppnå de nyttor ni eftersträvar.
      </BodyText>
      <BodyText size="lg" style={{ marginBottom: '24px', fontWeight: 'bold', color: 'inherit' }}>
        Välj vad du vill upphandla:
      </BodyText>
      <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
        <AddaButton variant="secondary" onClick={() => onNavigate && onNavigate('workstation')}>
          Resurser/Konsulter
        </AddaButton>
        <AddaButton variant="secondary" onClick={() => onNavigate && onNavigate('uppdrag')}>
          Uppdrag/Projekt
        </AddaButton>
      </div>
    </>
  );

  return (
    <LayoutLanding hero={heroContent}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: `${tokens.spacing['6xl']} ${tokens.spacing['4xl']}` 
      }}>
        
        {/* Pågående avrop */}
        <section style={{ marginBottom: tokens.spacing['6xl'] }}>
          <H2 style={{ marginBottom: tokens.spacing['4xl'], color: tokens.colors.neutral.text }}>
            Pågående avrop
          </H2>
          
          <ListItem
            backgroundColor={tokens.colors.neutral.surface}
            badge="Aktivt"
            badgeColor="green"
            title="IT-konsulter för digitaliseringsprojekt"
            description="Avrop av systemutvecklare och lösningsarkitekter för pågående digitalisering av medborgartjänster. Projektet löper till slutet av Q2 2025."
            metadata={[
              { icon: <Calendar size={16} />, text: 'Startdatum: 15 nov 2024' },
              { icon: <Users size={16} />, text: '3 konsulter' },
              { icon: <FileText size={16} />, text: 'Avropsnummer: 2024-0342' }
            ]}
            actionButton={
              <AddaButton size="small" onClick={() => window.location.href = '#/resurs-ws'}>
                Hantera avrop
              </AddaButton>
            }
          />
        </section>

        {/* Avslutade avrop */}
        <section>
          <H2 style={{ marginBottom: tokens.spacing['4xl'], color: tokens.colors.neutral.text }}>
            Avslutade avrop
          </H2>
          
          <ListItem
            backgroundColor={tokens.colors.neutral.surface}
            badge="Avslutat"
            badgeColor="blue"
            title="Projektledare för förvaltningsprojekt"
            description="Upphandling av certifierad projektledare för ledning av förvaltningsprojekt inom IT-infrastruktur."
            metadata={[
              { icon: <Calendar size={16} />, text: 'Avslutades: 30 sep 2024' },
              { icon: <Users size={16} />, text: '1 konsult' },
              { icon: <FileText size={16} />, text: 'Avropsnummer: 2024-0287' }
            ]}
            actionButton={
              <AddaButton size="small" variant="secondary">
                Visa detaljer
              </AddaButton>
            }
          />

          <ListItem
            backgroundColor={tokens.colors.neutral.surface}
            badge="Avslutat"
            badgeColor="blue"
            title="Arkitekter för systemmodernisering"
            description="Avrop av lösnings- och enterprisearkitekter för modernisering av ekonomisystem och integrationer."
            metadata={[
              { icon: <Calendar size={16} />, text: 'Avslutades: 15 aug 2024' },
              { icon: <Users size={16} />, text: '2 konsulter' },
              { icon: <FileText size={16} />, text: 'Avropsnummer: 2024-0201' }
            ]}
            actionButton={
              <AddaButton size="small" variant="secondary">
                Visa detaljer
              </AddaButton>
            }
          />

          <ListItem
            backgroundColor={tokens.colors.neutral.surface}
            badge="Avslutat"
            badgeColor="blue"
            title="Testledare för kvalitetssäkring"
            description="Upphandling av erfaren testledare för kvalitetssäkring av nya digitala tjänster inför lansering."
            metadata={[
              { icon: <Calendar size={16} />, text: 'Avslutades: 20 jun 2024' },
              { icon: <Users size={16} />, text: '1 konsult' },
              { icon: <FileText size={16} />, text: 'Avropsnummer: 2024-0156' }
            ]}
            actionButton={
              <AddaButton size="small" variant="secondary">
                Visa detaljer
              </AddaButton>
            }
          />
        </section>

      </div>
    </LayoutLanding>
  );
}

