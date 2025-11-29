import React from 'react';
import { tokens } from '../tokens';

export const AddaCard = ({ 
  children, 
  title,
  badge,
  date,
  image,
  onClick,
  bgColor = '#FFFFFF',
  className = '',
  style = {},
  ...props 
}) => {

  const baseStyle = {
    backgroundColor: bgColor,
    borderRadius: tokens.borderRadius.md, // Standard card radius (8px)
    boxShadow: tokens.shadows.card,
    border: `1px solid ${tokens.colors.neutral.border}`,
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    cursor: onClick ? 'pointer' : 'default',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    ...style
  };

  const handleMouseEnter = (e) => {
    if (!onClick) return;
    e.currentTarget.style.transform = 'translateY(-4px)';
    e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.12)';
  };

  const handleMouseLeave = (e) => {
    if (!onClick) return;
    e.currentTarget.style.transform = 'translateY(0)';
    e.currentTarget.style.boxShadow = tokens.shadows.card;
  };

  return (
    <div 
      style={baseStyle}
      onClick={onClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={className}
      {...props}
    >
      {image && (
        <div style={{
          width: '100%',
          height: '180px',
          overflow: 'hidden',
          backgroundColor: '#F5F5F5'
        }}>
          <img 
            src={image} 
            alt={title || ''}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              objectPosition: 'center'
            }}
          />
        </div>
      )}

      <div style={{ padding: '32px', display: 'flex', flexDirection: 'column', flex: 1 }}>
        {/* Date Badge */}
        {date && (
          <span style={{
            fontSize: tokens.typography.sizes.xs,
            fontWeight: tokens.typography.weights.bold,
            padding: `${tokens.spacing.xs} ${tokens.spacing.md}`,
            borderRadius: tokens.borderRadius.md, // MatcharListItem och ResourceSummaryCard (8px)
            backgroundColor: tokens.colors.ui.cardBgYellow,
            color: '#666',
            display: 'inline-block',
            marginBottom: tokens.spacing.xl,
            width: 'fit-content',
            fontFamily: tokens.typography.fontFamily
          }}>{date}</span>
        )}

        {/* Category/Status Badge */}
        {badge && (
          <span style={{
            fontSize: tokens.typography.sizes.xs,
            fontWeight: tokens.typography.weights.bold,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            padding: `${tokens.spacing.xs} ${tokens.spacing.md}`,
            borderRadius: tokens.borderRadius.md, // Matchar ListItem och ResourceSummaryCard (8px)
            backgroundColor: '#F5F5F5',
            color: '#666',
            display: 'inline-block',
            marginBottom: tokens.spacing.xl,
            width: 'fit-content',
            fontFamily: tokens.typography.fontFamily
          }}>{badge}</span>
        )}

        {/* Title */}
        {title && (
          <h3 style={{
            fontSize: '18px',
            fontWeight: tokens.typography.weights.bold,
            marginBottom: tokens.spacing.xl,
            color: tokens.colors.neutral.text,
            lineHeight: 1.3,
            fontFamily: tokens.typography.fontFamily
          }}>{title}</h3>
        )}

        {/* Content */}
        <div style={{
          color: '#666',
          fontSize: tokens.typography.sizes.sm,
          lineHeight: 1.6,
          fontFamily: tokens.typography.fontFamily,
          flex: 1
        }}>
          {children}
        </div>
      </div>
    </div>
  );
};

