import React from 'react';
import '../PBotMain.css'; 
import { tokens } from '../design-system/tokens';
import { ChevronUp } from 'lucide-react';
import addaLogo from '../assets/adda-header-logo-white.svg';

/**
 * Layout (Layout-komponent)
 * Denna komponent skapar den yttre ramen (Header, Footer, Grid) som 
 * omsluter allt innehåll.
 */
export default function Layout({ children, onShowDesignSystem }) {

    // --- Header (Förenklad för prototyp) ---
    const renderHeader = () => (
        <header style={{
            backgroundColor: tokens.colors.brand.primary, // #D32F00 (Röd)
            position: 'sticky',
            top: 0,
            zIndex: 100,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            width: '100%',
        }}>
            {/* Top Bar: Logotyp vänster, Verktyg höger */}
            <div style={{ 
                backgroundColor: tokens.colors.brand.primary,
                paddingTop: '16px',
                paddingBottom: '16px',
            }}>
            <div className="adda-container" style={{ 
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 1, minWidth: 0 }}>
                    <a href="/" title="Gå till startsidan, Adda.se">
                        <img 
                            src={addaLogo} 
                            alt="Adda.se logo" 
                            style={{ 
                                height: '48px',
                                maxWidth: '115px',
                            }} 
                        />
                    </a>
                </div>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexShrink: 0, marginLeft: '16px' }}>
                    {onShowDesignSystem && (
                        <a
                            href="#"
                            onClick={(e) => {
                                e.preventDefault();
                                onShowDesignSystem();
                            }}
                            style={{
                                color: tokens.colors.brand.lightTint,
                                textDecoration: 'none',
                                fontSize: '14px',
                                fontWeight: 500,
                                transition: 'opacity 0.2s',
                                cursor: 'pointer',
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                            onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                        >
                            Designsystem
                        </a>
                    )}
                    <button style={{
                        padding: '8px 16px',
                        borderRadius: tokens.borderRadius.pill,
                        fontSize: '14px',
                        fontWeight: 600,
                        backgroundColor: 'transparent',
                        color: '#FFFFFF',
                        border: '1px solid #FFFFFF',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        whiteSpace: 'nowrap',
                        flexShrink: 0
                    }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                        Logga in
                    </button>
                </div>
            </div>
            </div>
        </header>
    );

    // --- Footer (Uppdaterad utan vågform) ---
    const renderFooter = () => (
        <footer style={{
            backgroundColor: tokens.layout.footerBg, // Dark Petrol
            color: '#FFFFFF',
            position: 'relative',
            marginTop: '60px',
            width: '100%',
        }}>
            <div style={{
                padding: '24px 0',
            }}>
            <div className="adda-container" style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                    <div>
                        <button 
                            style={{
                                padding: '4px 16px',
                                backgroundColor: 'transparent',
                                border: '1px solid rgba(255, 255, 255, 0.3)',
                                color: '#FFFFFF',
                                borderRadius: tokens.borderRadius.pill,
                                cursor: 'pointer',
                                fontSize: '14px',
                                height: '32px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}
                            onClick={() => window.scrollTo(0, 0)}
                        >
                             <ChevronUp size={16} /> Till toppen
                        </button>
                    </div>
                </div>
            </div>
            </div>
        </footer>
    );

    return (
        <div id="adda-content-container" style={{ backgroundColor: tokens.colors.neutral.bg, minHeight: '100vh' }}>
            {renderHeader()}
            
            {/* Main har inte längre layout-wrapper, det delegeras till child-komponenten */}
            <main>
                {children} 
            </main>
            
            {renderFooter()}
        </div>
    );
}
