import React from 'react';
import { tokens } from '../tokens';

const TypeSpec = ({ component, htmlTag, size, weight, lineHeight, sample, color, usage }) => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingBottom: '24px', borderBottom: '1px solid #F0F0F0' }}>
    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
      <span style={{ fontFamily: 'monospace', fontSize: '14px', backgroundColor: tokens.colors.brand.lightTint, color: tokens.colors.brand.primary, padding: '4px 12px', borderRadius: '4px', fontWeight: 600 }}>{component}</span>
      <span style={{ fontFamily: 'monospace', fontSize: '12px', backgroundColor: '#F5F5F5', padding: '4px 8px', borderRadius: '4px' }}>&lt;{htmlTag}&gt;</span>
      <span style={{ fontFamily: 'monospace', fontSize: '12px', color: '#999' }}>{size} · {weight} · {lineHeight}</span>
    </div>
    <p style={{ fontSize: size, fontWeight: weight.split(' ')[0], color: color, margin: 0, lineHeight: 1.2 }}>{sample}</p>
    <p style={{ fontSize: '13px', color: '#666', margin: 0, fontStyle: 'italic' }}>{usage}</p>
  </div>
);

const TypographyDoc = () => {
  const typographyExamples = [
    { 
      component: 'H1', 
      htmlTag: 'h1', 
      size: tokens.typography.sizes['4xl'], 
      weight: `${tokens.typography.weights.bold} (Bold)`,
      lineHeight: tokens.typography.lineHeights.tight,
      sample: 'Vi säkrar framtidens välfärd genom smarta inköp', 
      color: tokens.colors.brand.primary,
      usage: 'Användning: Hero-rubriker, sidtitlar. Endast en H1 per sida för tillgänglighet (WCAG).'
    },
    { 
      component: 'H2', 
      htmlTag: 'h2', 
      size: tokens.typography.sizes['2xl'], 
      weight: `${tokens.typography.weights.bold} (Bold)`,
      lineHeight: tokens.typography.lineHeights.normal,
      sample: 'Aktuellt från Adda', 
      color: tokens.colors.neutral.text,
      usage: 'Användning: Sektionsrubriker, huvudrubriker i innehållsområden.'
    },
    { 
      component: 'H3', 
      htmlTag: 'h3', 
      size: tokens.typography.sizes.xl, 
      weight: `${tokens.typography.weights.semibold} (Semibold)`,
      lineHeight: tokens.typography.lineHeights.normal,
      sample: 'Nytt ramavtal för krisberedskap klart', 
      color: tokens.colors.neutral.text,
      usage: 'Användning: Underrubriker, kortrubriker, grupprubriker.'
    },
    { 
      component: 'H4', 
      htmlTag: 'h4', 
      size: tokens.typography.sizes.lg, 
      weight: `${tokens.typography.weights.semibold} (Semibold)`,
      lineHeight: tokens.typography.lineHeights.normal,
      sample: 'Kontaktuppgifter', 
      color: tokens.colors.neutral.text,
      usage: 'Användning: Mindre rubriker, formulärgrupper, sidebar-rubriker.'
    },
    { 
      component: 'BodyText', 
      htmlTag: 'p', 
      size: tokens.typography.sizes.base, 
      weight: `${tokens.typography.weights.regular} (Regular)`,
      lineHeight: tokens.typography.lineHeights.relaxed,
      sample: 'Vi hjälper dig att göra hållbara affärer. Sök bland våra ramavtal och hitta rätt lösning för din verksamhet.', 
      color: tokens.colors.neutral.text,
      usage: 'Användning: Brödtext, beskrivningar, längre textavsnitt. Prop: size="sm|base|lg", bold={true|false}'
    },
    { 
      component: 'Caption', 
      htmlTag: 'span', 
      size: tokens.typography.sizes.sm, 
      weight: `${tokens.typography.weights.regular} (Regular)`,
      lineHeight: tokens.typography.lineHeights.normal,
      sample: 'Senast uppdaterad: 2024-01-15', 
      color: tokens.colors.neutral.lightGrey,
      usage: 'Användning: Hjälptext, metadata, tidsstämplar, fotnoter.'
    },
  ];

  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Typografi</h2>
      <div style={{ backgroundColor: '#FFFFFF', padding: '32px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
        <div style={{ marginBottom: '32px', paddingBottom: '32px', borderBottom: '1px solid #E5E5E5' }}>
          <div style={{ fontSize: '14px', color: '#999', fontFamily: 'monospace', marginBottom: '8px' }}>Font Family</div>
          <div style={{ fontSize: '36px', fontWeight: 'bold' }}>Avenir Next</div>
          <div style={{ color: '#666', marginTop: '8px' }}>Fallback: Helvetica, Arial, sans-serif</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {typographyExamples.map((example, idx) => (
            <TypeSpec 
              key={idx}
              component={example.component}
              htmlTag={example.htmlTag}
              size={example.size} 
              weight={example.weight} 
              lineHeight={example.lineHeight}
              sample={example.sample}
              color={example.color}
              usage={example.usage}
            />
          ))}
        </div>

        <div style={{ marginTop: '32px', paddingTop: '32px', borderTop: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px' }}>Font Weights i användning</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px' }}>
            {Object.entries(tokens.typography.weights).map(([name, weight]) => (
              <div key={name} style={{ padding: '16px', backgroundColor: '#F5F5F5', borderRadius: '8px' }}>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '4px' }}>{name}</div>
                <div style={{ fontSize: '24px', fontWeight: weight }}>{weight}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypographyDoc;



