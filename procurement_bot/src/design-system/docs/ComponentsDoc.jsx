import React from 'react';
import { FileText, GraduationCap, ShoppingCart, Leaf, ArrowUp } from 'lucide-react';
import { tokens } from '../tokens';
import { AddaButton } from '../components/AddaButton';
import { AddaCard } from '../components/AddaCard';
import { AddaInput, AddaSelect } from '../components/AddaInput';
import { default as SystemNotice } from '../components/SystemNotice';
import { PageTitle } from '../components/PageTitle';
import { default as ResourceSummaryCard } from '../components/ResourceSummaryCard';
import { default as DebugCard } from '../components/DebugCard';
import { default as SummaryCard } from '../components/SummaryCard';

// Simple Card component for demo
const Card = ({ badge, date, title, desc }) => (
  <div style={{
    backgroundColor: tokens.colors.neutral.surface,
    borderRadius: tokens.borderRadius.lg,
    overflow: 'hidden',
    boxShadow: tokens.shadows.card
  }}>
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
        <span style={{
          fontSize: '12px',
          fontWeight: 600,
          padding: '4px 12px',
          borderRadius: tokens.borderRadius.pill,
          backgroundColor: tokens.colors.ui.iconBg,
          color: tokens.colors.brand.secondary
        }}>{badge}</span>
        <span style={{ fontSize: '12px', color: '#999' }}>{date}</span>
      </div>
      <h4 style={{ fontWeight: 'bold', fontSize: '18px', marginBottom: '8px', color: tokens.colors.neutral.text }}>{title}</h4>
      <p style={{ fontSize: '14px', color: '#666', lineHeight: 1.5 }}>{desc}</p>
    </div>
  </div>
);

const ComponentsDoc = () => {
  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Atomära Komponenter</h2>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '32px' }}>
        {/* BUTTONS */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Knappar (Pill Shape)</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Primary CTA */}
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px' }}>
              <AddaButton variant="primary">Primary CTA</AddaButton>
              <span style={{ fontSize: '12px', color: '#999', fontFamily: 'monospace' }}>
                Radius: {tokens.borderRadius.pill}
              </span>
            </div>
            
            {/* Secondary */}
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px' }}>
              <AddaButton variant="secondary">Secondary</AddaButton>
              <span style={{ fontSize: '12px', color: '#999', fontFamily: 'monospace' }}>
                Outline style
              </span>
            </div>
            
            {/* Login button */}
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px' }}>
              <div style={{ backgroundColor: tokens.colors.brand.primary, padding: '8px', borderRadius: '4px' }}>
                <AddaButton variant="outline" size="small">Logga in</AddaButton>
              </div>
              <span style={{ fontSize: '12px', color: '#999', fontFamily: 'monospace' }}>
                White outline on primary
              </span>
            </div>

            {/* Send Button */}
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '16px' }}>
              <AddaButton variant="sendButton">
                <ArrowUp size={24} color={tokens.colors.brand.lightTint} />
              </AddaButton>
              <span style={{ fontSize: '12px', color: '#999', fontFamily: 'monospace' }}>
                variant="sendButton" (40px Circle)
              </span>
            </div>
          </div>
        </div>

        {/* ICON CIRCLES */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Icon Circles</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', alignItems: 'center' }}>
            {[
              { icon: <FileText size={32} strokeWidth={2} />, name: 'FileText' },
              { icon: <GraduationCap size={32} strokeWidth={2} />, name: 'GraduationCap' },
              { icon: <ShoppingCart size={32} strokeWidth={2} />, name: 'ShoppingCart' },
              { icon: <Leaf size={32} strokeWidth={2} />, name: 'Leaf' }
            ].map((item, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: tokens.borderRadius.iconCircle,
                  backgroundColor: tokens.colors.ui.iconBg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <div style={{ color: tokens.colors.ui.iconColor }}>
                    {item.icon}
                  </div>
                </div>
                <span style={{ fontSize: '11px', color: '#999', fontFamily: 'monospace' }}>
                  {item.name}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* INPUTS & SELECTS */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Formulär</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <AddaInput 
                label="Input Field" 
                placeholder="Ange text..."
              />
            </div>
            <div>
              <AddaSelect 
                label="Select Dropdown" 
                options={[{ label: 'Alternativ 1', value: '1' }, { label: 'Alternativ 2', value: '2' }]} 
              />
            </div>
          </div>
        </div>

        {/* CARDS */}
        <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '24px', borderRadius: '12px', border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Kort & Radius</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
            {/* 0px Radius */}
            <div>
              <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>Radius: 0px (none)</div>
              <AddaCard 
                style={{ borderRadius: tokens.borderRadius.none }}
                title="Rektangulärt (0px)"
              >
                Används för element som ligger kant-i-kant eller i listor.
              </AddaCard>
            </div>

            {/* 8px Radius */}
            <div>
              <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>Radius: 8px (md)</div>
              <AddaCard 
                style={{ borderRadius: tokens.borderRadius.md }}
                title="Standard (8px)"
            badge="Kategori"
                date="2023-10-27"
              >
                Standard för de flesta kort, paneler och formulärelement i applikationen.
              </AddaCard>
            </div>

            {/* 16px Radius */}
            <div>
              <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>Radius: 16px (lg)</div>
              <AddaCard 
                style={{ borderRadius: tokens.borderRadius.lg }}
                title="Large (16px)"
                badge="Nyhet"
                date="Idag"
              >
                Används för fristående element, dialogrutor och mer "mjuka" UI-delar som chattbubblor.
              </AddaCard>
            </div>
          </div>
        </div>

        {/* --- NYA SEKTIONER --- */}

        {/* PageTitle */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>PageTitle</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>Standardiserad sidrubrik med valfri underrubrik.</p>
          <div style={{ padding: '24px', border: `1px dashed ${tokens.colors.neutral.border}`, borderRadius: '8px' }}>
            <PageTitle 
              title="Resursupphandling" 
              subtitle="Steg 1: Behovsanalys" 
            />
          </div>
        </div>

        {/* SystemNotice */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>SystemNotice</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>Notiser för systemmeddelanden, varningar eller information.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <SystemNotice type="info">Detta är en informationsnotis.</SystemNotice>
            <SystemNotice type="warning">Detta är en varningsnotis.</SystemNotice>
            <SystemNotice type="error">Detta är en felnotis.</SystemNotice>
            <SystemNotice type="success">Detta är en framgångsnotis.</SystemNotice>
          </div>
        </div>

        {/* ProcessProgressBar REMOVED - Moved to ChatDoc */}

        {/* Sammansatta Komponenter */}
        <div style={{ marginTop: tokens.spacing['4xl'], marginBottom: tokens.spacing.xl }}>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold' }}>Sammansatta Komponenter</h2>
          <p style={{ color: '#666' }}>Komplexa komponenter byggda av flera atomära delar.</p>
        </div>

        {/* ResourceSummaryCard */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ResourceSummaryCard</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>Sammanfattningskort för en resursroll.</p>
          <div style={{ maxWidth: '400px' }}>
            <ResourceSummaryCard 
              role="Systemutvecklare"
              quantity={2}
              level="Nivå 4"
              location="Stockholm"
              description="Erfaren Java-utvecklare med fokus på backend."
            />
          </div>
        </div>

        {/* DebugCard */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>DebugCard (Dev Only)</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>Kort för att visa debug-data i utvecklingsläge.</p>
          <DebugCard data={{ state: 'active', user_id: 123, roles: ['admin', 'editor'] }} title="Session State" />
        </div>

        {/* SummaryCard (Varukorgen) */}
        <div style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5', gridColumn: 'span 2' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>SummaryCard ("Varukorgen")</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Visar en sammanfattning av användarens förfrågan med stöd för <strong>flera resurser</strong> (team-beställningar). 
            Resurser med både roll och nivå markeras som DONE, övriga som PENDING.
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            {/* Empty State */}
            <div>
              <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>Empty State</div>
              <SummaryCard 
                data={{
                  resources: [],
                  location: null,
                  volume: null,
                  start_date: null,
                  price_cap: null
                }}
                title="Din Förfrågan"
              />
            </div>

            {/* Partially Filled */}
            <div>
              <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>Partially Filled (PENDING)</div>
              <SummaryCard 
                data={{
                  resources: [
                    { id: "res_1", role: "Projektledare", level: 4, quantity: 1, status: "DONE" },
                    { id: "res_2", role: "Utvecklare", level: null, quantity: 2, status: "PENDING" }
                  ],
                  location: "Stockholm",
                  volume: null,
                  start_date: null,
                  price_cap: null
                }}
                title="Din Förfrågan"
              />
            </div>

            {/* Fully Filled */}
            <div>
              <div style={{ marginBottom: '8px', fontSize: '12px', color: '#666', fontFamily: 'monospace' }}>Fully Filled (All DONE)</div>
              <SummaryCard 
                data={{
                  resources: [
                    { id: "res_1", role: "Projektledare", level: 4, quantity: 1, status: "DONE" },
                    { id: "res_2", role: "Utvecklare", level: 3, quantity: 2, status: "DONE" },
                    { id: "res_3", role: "Testare", level: 2, quantity: 1, status: "DONE" }
                  ],
                  location: "Stockholm",
                  volume: "500 timmar",
                  start_date: "2025-06-01",
                  price_cap: "1200 kr/h"
                }}
                title="Din Förfrågan"
              />
            </div>
          </div>

          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> data (resources[], location, volume, start_date, price_cap), title, style
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComponentsDoc;



