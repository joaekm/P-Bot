import React from 'react';
import { Calendar, MapPin } from 'lucide-react';
import { tokens } from '../tokens';
import { ListItem } from '../list';

const ListDoc = () => {
  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>List & Filter Komponenter</h2>
      <p style={{ color: '#666', marginBottom: '32px' }}>
        Komponenter för listningar, filtrering och sökning, inspirerade av adda.se/utbildningar.
      </p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* Badge Colors */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Badge Färger</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>Färgkodade badges för kategorier i listningar.</p>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px' }}>
            {[
              { name: 'Yellow', color: tokens.colors.ui.cardBgYellow },
              { name: 'Blue', color: tokens.colors.ui.cardBgBlue },
              { name: 'Green', color: tokens.colors.ui.cardBgGreen },
              { name: 'Pink', color: tokens.colors.ui.cardBgPink },
              { name: 'Orange', color: tokens.colors.ui.cardBgOrange }
            ].map((badge, idx) => (
              <div key={idx} style={{
                padding: '8px 16px',
                backgroundColor: badge.color,
                color: '#333',
                borderRadius: tokens.borderRadius.md,
                fontSize: '14px',
                fontWeight: 600
              }}>
                {badge.name}
              </div>
            ))}
          </div>
        </section>

        {/* ListItem Variants */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ListItem - Olika bakgrundsfärger</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>Kompakt kort för listobjekt med badge, metadata och åtgärdsknapp.</p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <ListItem 
              badge="Nyhet"
              badgeColor={tokens.colors.ui.cardBgOrange}
              title="Nya riktlinjer för hållbar upphandling 2025"
              description="SKR har publicerat uppdaterade riktlinjer för hur offentlig sektor ska arbeta med hållbar upphandling."
              date="10 dec 2024"
              bgColor={tokens.colors.neutral.surface}
            />
            
            <ListItem 
              badge="Ekonomi"
              badgeColor={tokens.colors.ui.cardBgYellow}
              title="Grundläggande upphandling – steg för steg"
              description="Lär dig grunderna i offentlig upphandling. Kursen ger dig verktygen för att genomföra korrekta upphandlingar."
              date="15 jan 2025"
              location="Stockholm"
              bgColor={tokens.colors.neutral.bg}
            />
            
            <ListItem 
              badge="Hållbarhet"
              badgeColor={tokens.colors.ui.cardBgGreen}
              title="Miljökrav i upphandling"
              description="Hur du ställer effektiva miljökrav och följer upp dem."
              date="20 jan 2025"
              location="Digitalt"
              bgColor={tokens.colors.brand.bgHero}
            />
            
            <ListItem 
              badge="IT"
              badgeColor={tokens.colors.ui.cardBgBlue}
              title="IT-säkerhet vid upphandling"
              description="Grundläggande kurs om säkerhetskrav vid IT-upphandlingar."
              date="25 jan 2025"
              bgColor={tokens.colors.ui.iconBg}
            />
          </div>
        </section>
      </div>
    </div>
  );
};

export default ListDoc;



