import React from 'react';
import { AlertCircle, Check } from 'lucide-react';
import { tokens } from '../tokens';

const ColorSwatch = ({ name, hex, usage, darkText }) => (
  <div style={{
    backgroundColor: '#FFFFFF',
    padding: '12px',
    borderRadius: '8px',
    boxShadow: tokens.shadows.card,
    display: 'flex',
    flexDirection: 'column',
    border: '1px solid #E5E5E5'
  }}>
    <div 
      style={{
        height: '80px',
        width: '100%',
        borderRadius: '6px',
        marginBottom: '12px',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: hex
      }}
    >
      {darkText && <Check style={{ color: 'rgba(0, 0, 0, 0.2)' }} size={24} />}
      {!darkText && <Check style={{ color: 'rgba(255, 255, 255, 0.2)' }} size={24} />}
    </div>
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <span style={{ fontWeight: 'bold', fontSize: '14px', color: '#333', marginBottom: '4px' }}>{name}</span>
      <span style={{ fontFamily: 'monospace', fontSize: '12px', color: '#666', backgroundColor: '#F5F5F5', padding: '2px 4px', borderRadius: '2px', width: 'fit-content', marginBottom: '8px' }}>{hex}</span>
      <span style={{ fontSize: '10px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{usage}</span>
    </div>
  </div>
);

const ColorsDoc = () => {
  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Färgpalett</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        <section>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '24px', borderRadius: '4px', backgroundColor: tokens.colors.brand.primary }}></div>
            Brand Colors
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <ColorSwatch name="Primary (Röd)" hex={tokens.colors.brand.primary} usage="Header, CTA, Logotyp" />
            <ColorSwatch name="Secondary (Petrol)" hex={tokens.colors.brand.secondary} usage="Footer, Rubriker, Ikoner" />
            <ColorSwatch name="Hero Background" hex={tokens.colors.brand.bgHero} usage="Hero-ytor, Pastell" darkText />
            <ColorSwatch name="Icon Background (Ice Teal)" hex={tokens.colors.ui.iconBg} usage="Bakgrundscirklar för ikoner" darkText />
          </div>
        </section>

        <section>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '24px', borderRadius: '4px', backgroundColor: tokens.colors.accent.darkRed }}></div>
            Accent Colors
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <ColorSwatch name="Dark Red" hex={tokens.colors.accent.darkRed} usage="Meny bakgrund" />
            <ColorSwatch name="Dark Petrol" hex={tokens.colors.accent.darkPetrol} usage="Footer bakgrund" />
          </div>
        </section>

        <section>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '24px', borderRadius: '4px', backgroundColor: tokens.colors.neutral.bg }}></div>
            Neutral & Surfaces
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <ColorSwatch name="Warm Background" hex={tokens.colors.neutral.bg} usage="Section Backgrounds" darkText />
            <ColorSwatch name="Text (Dark Grey)" hex={tokens.colors.neutral.text} usage="Headings, Body" />
            <ColorSwatch name="Border" hex={tokens.colors.neutral.border} usage="Inputs, Borders" darkText />
            <ColorSwatch name="Grey" hex={tokens.colors.neutral.grey} usage="Secondary text" />
          </div>
        </section>

        <section>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>UI Colors</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
            <ColorSwatch name="Card Yellow" hex={tokens.colors.ui.cardBgYellow} usage="Produktkort kategori" darkText />
            <ColorSwatch name="Card Blue" hex={tokens.colors.ui.cardBgBlue} usage="Produktkort kategori" darkText />
            <ColorSwatch name="Icon Background" hex={tokens.colors.ui.iconBg} usage="Bakgrundscirklar" darkText />
            <ColorSwatch name="Icon Color" hex={tokens.colors.ui.iconColor} usage="Ikonfärg" />
          </div>
        </section>

        <div style={{
          backgroundColor: '#E3F2FD',
          padding: '16px',
          borderRadius: tokens.borderRadius.lg,
          border: '1px solid #BBDEFB',
          display: 'flex',
          gap: '12px',
          alignItems: 'flex-start'
        }}>
          <AlertCircle style={{ color: '#1976D2', flexShrink: 0, marginTop: '4px' }} size={20} />
          <div>
            <h4 style={{ fontWeight: 'bold', color: '#0D47A1', marginBottom: '4px' }}>Designaudit</h4>
            <p style={{ fontSize: '14px', color: '#1565C0', marginTop: '4px' }}>
              <strong>Röd (#D32F00)</strong> är den dominerande identitetsbäraren (Header/Logotyp/CTA), 
              medan <strong>Petrol (#005B59)</strong> är den bärande strukturfärgen (Footer/Text/Ikoner).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ColorsDoc;




