// Fil: procurement_bot/src/App.jsx
// Huvudapplikation med routing mellan sidor och designsystem

import React, { useState, useEffect } from 'react';
import Layout from './app/Layout';
import {
  Dashboard,
  ResursWorkstation,
  Uppdrag,
  ResursResultat,
  UppdragResultat,
  FkuProcess,
  FkuWorkstation,
  DrProcess
} from './app/pages';
import './PBotMain.css';

// Importera designsystemets dokumentation
import { DesignSystemShell } from './design-system/docs';

function App() {
  const [showDesignSystem, setShowDesignSystem] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard');

  // Hantera sidtitel och scroll
  useEffect(() => {
    window.scrollTo(0, 0);
    if (!showDesignSystem) {
      document.title = 'Adda - Avropsassistent';
    }
  }, [currentView, showDesignSystem]);

  // Om designsystemet ska visas, visa bara det
  if (showDesignSystem) {
    return (
      <div>
        <div style={{ position: 'fixed', top: '1rem', right: '1rem', zIndex: 1000 }}>
          <button 
            onClick={() => {
              setShowDesignSystem(false);
              setCurrentView('dashboard');
            }}
            className="adda-button adda-button--secondary"
            style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
          >
            ← Tillbaka till Prototyp
          </button>
        </div>
        <DesignSystemShell />
      </div>
    );
  }

  // Render rätt vy baserat på currentView
  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentView} />;
      case 'uppdrag':
        return <Uppdrag />;
      case 'workstation':
        return <ResursWorkstation />;
      case 'resurs_resultat':
        return <ResursResultat />;
      case 'uppdrag_resultat':
        return <UppdragResultat />;
      case 'fku_process':
        return <FkuProcess />;
      case 'fku_ws':
        return <FkuWorkstation />;
      case 'dr_process':
        return <DrProcess />;
      default:
        return <Dashboard onNavigate={setCurrentView} />;
    }
  };

  return (
    <Layout onShowDesignSystem={() => setShowDesignSystem(true)}>
      {renderView()}
    </Layout>
  );
}

export default App;
