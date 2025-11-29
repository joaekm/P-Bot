import React from 'react';
import { tokens } from '../tokens';

const LayoutDoc = () => {
  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Layout & Grid System</h2>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {/* Grid System */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px' }}>Grid System (12-kolumns)</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                Standard Grid - 12 kolumner
              </div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: `repeat(${tokens.layout.gridColumns}, 1fr)`,
                gap: tokens.layout.gridGap,
                padding: '16px',
                backgroundColor: '#F5F5F5',
                borderRadius: '8px'
              }}>
                {Array.from({length: tokens.layout.gridColumns}).map((_, i) => (
                  <div key={i} style={{
                    height: '32px',
                    backgroundColor: tokens.colors.brand.light,
                    borderRadius: '4px',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: tokens.colors.brand.primary,
                    fontWeight: 'bold'
                  }}>
                    {i + 1}
                  </div>
                ))}
              </div>
              <div style={{ fontSize: '12px', color: '#999', fontFamily: 'monospace', marginTop: '8px' }}>
                Columns: {tokens.layout.gridColumns} | Gap: {tokens.layout.gridGap}
              </div>
            </div>
          </div>
        </section>

        {/* Container System */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px' }}>Container System</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px' }}>
              <div style={{ fontSize: '14px', marginBottom: '4px' }}>
                <strong>Max Width:</strong> <code style={{ backgroundColor: '#FFFFFF', padding: '2px 8px', borderRadius: '4px' }}>{tokens.layout.containerMaxWidth}</code>
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                Padding: 24px left/right | Margin: 0 auto
              </div>
            </div>
          </div>
        </section>

        {/* Spacing System */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px' }}>Spacing System</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '16px' }}>
            {Object.entries(tokens.spacing).map(([name, value]) => (
              <div key={name} style={{ padding: '16px', backgroundColor: '#F5F5F5', borderRadius: '8px' }}>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>{name}</div>
                <div style={{ height: '16px', backgroundColor: tokens.colors.brand.primary, borderRadius: '4px', marginBottom: '8px', width: value }}></div>
                <div style={{ fontSize: '14px', fontFamily: 'monospace' }}>{value}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Border Radius */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px' }}>Border Radius</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px' }}>
            {Object.entries(tokens.borderRadius).map(([name, value]) => (
              <div key={name} style={{ padding: '16px', backgroundColor: '#F5F5F5', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  margin: '0 auto 8px',
                  backgroundColor: tokens.colors.brand.primary,
                  borderRadius: value
                }}></div>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>{name}</div>
                <div style={{ fontSize: '14px', fontFamily: 'monospace' }}>{value}</div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default LayoutDoc;



