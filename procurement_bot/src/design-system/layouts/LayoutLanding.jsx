import React from 'react';
import { tokens } from '../tokens';

const LayoutLanding = ({ hero, children }) => {
  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Hero Section - Full Width */}
      {hero && (
        <div style={{ width: '100%', marginBottom: tokens.spacing['6xl'] }}>
          {hero}
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

