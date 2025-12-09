import React from 'react';
import { tokens } from '../tokens';

const LayoutLanding = ({ hero, children }) => {
  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Hero Section - Mörkröd bakgrundsfärg, vit text, centrerat innehåll */}
      {hero && (
        <div style={{ 
          width: '100%',
          backgroundColor: tokens.colors.accent.darkRed,
          color: '#FFFFFF',
          marginBottom: tokens.spacing['6xl'],
          paddingTop: tokens.spacing['6xl'],
          paddingBottom: tokens.spacing['6xl'],
          paddingLeft: '24px',
          paddingRight: '24px',
          boxSizing: 'border-box',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <div style={{
            maxWidth: '700px',
            width: '100%',
            textAlign: 'center'
          }}>
            {hero}
          </div>
        </div>
      )}

      {/* Main Content - Centered Container using adda-container-system */}
      <div className="adda-container-system">
        {children}
      </div>
    </div>
  );
};

export default LayoutLanding;

