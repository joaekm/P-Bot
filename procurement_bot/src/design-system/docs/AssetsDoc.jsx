import React from 'react';
import { AlertCircle } from 'lucide-react';
import { tokens } from '../tokens';
import addaLogo from '../../assets/adda-header-logo-white.svg';
import heroImage from '../../assets/utbildning-for-fler-hero-2550x850.webp';
import cardImage1 from '../../assets/digitala-enheter-for-arbetsplats-och-skola-2024---2400x600.webp';
import cardImage2 from '../../assets/upphandling-och-ramavtal-786.webp';
import cardImage3 from '../../assets/lores-upphandlingsplan-sidbild-800.webp';
import personaImageUrl from '../../assets/adda_assistent.png';

const AssetsDoc = () => {
  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Assets & Logos</h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {/* Logo */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Logotyp</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', alignItems: 'center' }}>
            <div style={{
              padding: '24px 32px',
              backgroundColor: tokens.colors.brand.primary,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <img 
                src={addaLogo} 
                alt="Adda logo" 
                style={{ height: '48px', filter: 'brightness(0) invert(1)' }}
              />
            </div>
            <div style={{
              padding: '24px 32px',
              backgroundColor: tokens.colors.brand.secondary,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <img 
                src={addaLogo} 
                alt="Adda logo" 
                style={{ height: '48px', filter: 'brightness(0) invert(1)' }}
              />
            </div>
          </div>
          <div style={{ marginTop: '16px', fontSize: '12px', color: '#999', fontFamily: 'monospace' }}>
            assets/adda-header-logo-white.svg
          </div>
        </section>

        {/* Assistant Avatar */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Assistent Avatar</h3>
          <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
            <img 
              src={personaImageUrl} 
              alt="Adda Assistent" 
              style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%',
                border: `3px solid ${tokens.colors.neutral.border}`
              }}
            />
            <div>
              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>Adda Assistent</div>
              <div style={{ fontSize: '14px', color: '#666' }}>Används i chattgränssnitt</div>
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999', fontFamily: 'monospace' }}>
                assets/adda_assistent.png
              </div>
            </div>
          </div>
        </section>

        {/* Hero Images */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Hero & Kortbilder</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
            <div>
              <img 
                src={heroImage} 
                alt="Hero" 
                style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '8px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>Hero image</div>
            </div>
            <div>
              <img 
                src={cardImage1} 
                alt="Card 1" 
                style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '8px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>Card image 1</div>
            </div>
            <div>
              <img 
                src={cardImage2} 
                alt="Card 2" 
                style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '8px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>Card image 2</div>
            </div>
            <div>
              <img 
                src={cardImage3} 
                alt="Card 3" 
                style={{ width: '100%', height: '120px', objectFit: 'cover', borderRadius: '8px' }}
              />
              <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>Card image 3</div>
            </div>
          </div>
        </section>

        {/* Info Box */}
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
            <h4 style={{ fontWeight: 'bold', color: '#0D47A1', marginBottom: '4px' }}>Om assets</h4>
            <p style={{ fontSize: '14px', color: '#1565C0', marginTop: '4px' }}>
              Alla assets finns i <code style={{ backgroundColor: '#FFFFFF', padding: '2px 4px', borderRadius: '2px' }}>src/assets/</code>-mappen.
              Lägg till nya bilder där och importera dem i komponenterna.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssetsDoc;



