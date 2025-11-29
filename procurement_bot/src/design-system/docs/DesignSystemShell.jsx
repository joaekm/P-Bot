import React, { useState, useEffect } from 'react';
import { Type, Palette, Box, Layout, Monitor, MessageSquare, List } from 'lucide-react';
import { tokens } from '../tokens';

// Import doc pages
import ColorsDoc from './ColorsDoc';
import TypographyDoc from './TypographyDoc';
import ComponentsDoc from './ComponentsDoc';
import ChatDoc from './ChatDoc';
import ListDoc from './ListDoc';
import LayoutDoc from './LayoutDoc';
import AssetsDoc from './AssetsDoc';
import LayoutsPreviewDoc from './LayoutsPreviewDoc';

/**
 * ADDA DESIGN SYSTEM - Documentation Shell
 * Navigation sidebar + content area for design system documentation
 */
const DesignSystemShell = () => {
  const [activeTab, setActiveTab] = useState('layouts_preview');

  useEffect(() => {
    document.title = 'Adda - Designsystem';
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'layouts_preview':
        return <LayoutsPreviewDoc />;
      case 'colors':
        return <ColorsDoc />;
      case 'typography':
        return <TypographyDoc />;
      case 'components':
        return <ComponentsDoc />;
      case 'chat':
        return <ChatDoc />;
      case 'listfilter':
        return <ListDoc />;
      case 'layout':
        return <LayoutDoc />;
      case 'assets':
        return <AssetsDoc />;
      default:
        return <LayoutsPreviewDoc />;
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      fontFamily: tokens.typography.fontFamily,
      color: tokens.colors.neutral.text,
      backgroundColor: tokens.colors.neutral.bg,
      display: 'flex',
      flexDirection: 'row'
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700&display=swap');
        body { font-family: ${tokens.typography.fontFamily}, 'Nunito Sans', sans-serif; }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .adda-grid-system {
          display: grid;
          grid-template-columns: repeat(${tokens.layout.gridColumns}, 1fr);
          gap: ${tokens.layout.gridGap};
        }
        
        .adda-layout-grid {
          display: flex;
          flex-direction: column;
          gap: ${tokens.layout.gridGap};
          align-items: start;
        }
        
        .adda-col-main { width: 100%; }
        .adda-col-sidebar { width: 100%; }

        @media (min-width: ${tokens.layout.breakpoints.desktop}) {
          .adda-layout-grid {
            display: grid;
            grid-template-columns: repeat(${tokens.layout.gridColumns}, 1fr);
            align-items: start;
          }
          .adda-col-main { grid-column: span 8; }
          .adda-col-sidebar { grid-column: span 4; }
        }
        
        .adda-container-system {
          max-width: ${tokens.layout.containerMaxWidth};
          margin: 0 auto;
          padding-left: 24px;
          padding-right: 24px;
        }
      `}</style>

      {/* SIDEBAR */}
      <aside style={{
        width: '288px',
        backgroundColor: '#FFFFFF',
        borderRight: '1px solid #E5E5E5',
        flexShrink: 0,
        height: '100vh',
        position: 'sticky',
        top: 0,
        overflowY: 'auto'
      }}>
        <div style={{ padding: '24px', borderBottom: '1px solid #E5E5E5' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontWeight: 'bold',
              fontSize: '20px',
              backgroundColor: tokens.colors.brand.primary
            }}>A</div>
            <div>
              <h1 style={{ fontWeight: 'bold', fontSize: '18px', lineHeight: '1.2' }}>Adda Design</h1>
              <span style={{ fontSize: '12px', color: '#666', fontWeight: 500, padding: '2px 8px', backgroundColor: '#F5F5F5', borderRadius: '999px' }}>v5.0</span>
            </div>
          </div>
        </div>
        
        <nav style={{ padding: '16px' }}>
          <NavItem icon={<Monitor size={18} />} label="Sid-layouter" active={activeTab === 'layouts_preview'} onClick={() => setActiveTab('layouts_preview')} />
          
          <div style={{ marginTop: '24px', marginBottom: '8px', paddingLeft: '12px', fontSize: '12px', fontWeight: 'bold', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Tokens</div>
          <NavItem icon={<Palette size={18} />} label="Färger & Palett" active={activeTab === 'colors'} onClick={() => setActiveTab('colors')} />
          <NavItem icon={<Type size={18} />} label="Typografi" active={activeTab === 'typography'} onClick={() => setActiveTab('typography')} />
          
          <div style={{ marginTop: '24px', marginBottom: '8px', paddingLeft: '12px', fontSize: '12px', fontWeight: 'bold', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Komponenter</div>
          <NavItem icon={<Box size={18} />} label="Atomära Komponenter" active={activeTab === 'components'} onClick={() => setActiveTab('components')} />
          <NavItem icon={<MessageSquare size={18} />} label="Chattkomponenter" active={activeTab === 'chat'} onClick={() => setActiveTab('chat')} />
          <NavItem icon={<List size={18} />} label="List & Filter" active={activeTab === 'listfilter'} onClick={() => setActiveTab('listfilter')} />
          <NavItem icon={<Layout size={18} />} label="Layout & Grid" active={activeTab === 'layout'} onClick={() => setActiveTab('layout')} />
          <NavItem icon={<Palette size={18} />} label="Assets & Logos" active={activeTab === 'assets'} onClick={() => setActiveTab('assets')} />
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main style={{
        flex: 1,
        overflowY: 'auto',
        backgroundColor: tokens.colors.neutral.bg
      }}>
        <div className="adda-container-system" style={{ padding: '32px' }}>
          {renderContent()}
        </div>
      </main>
    </div>
  );
};

// Navigation Item Component
const NavItem = ({ icon, label, active, onClick }) => (
  <button 
    onClick={onClick}
    style={{
      width: '100%',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '10px 12px',
      borderRadius: '6px',
      fontSize: '14px',
      fontWeight: 500,
      transition: 'all 0.2s',
      backgroundColor: active ? tokens.colors.brand.primary : 'transparent',
      color: active ? '#FFFFFF' : '#666',
      border: 'none',
      cursor: 'pointer',
      textAlign: 'left'
    }}
    onMouseEnter={(e) => {
      if (!active) e.currentTarget.style.backgroundColor = '#F5F5F5';
    }}
    onMouseLeave={(e) => {
      if (!active) e.currentTarget.style.backgroundColor = 'transparent';
    }}
  >
    {icon}
    {label}
  </button>
);

export default DesignSystemShell;



