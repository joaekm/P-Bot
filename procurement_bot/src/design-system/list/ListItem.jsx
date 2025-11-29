import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../../utils/tokens';

/**
 * ListItem - Kompakt kortkomponent för listobjekt
 * 
 * @param {string} badge - Badge-text
 * @param {string} badgeColor - Badge-färg (yellow, blue, green, pink, orange eller hex)
 * @param {string} title - Titel
 * @param {string} description - Beskrivning
 * @param {array} metadata - Array av metadata: [{ icon, text }]
 * @param {node} actionButton - Action button komponent
 * @param {function} onClick - Callback när hela kortet klickas
 * @param {string} accentColor - Färg för vänster accent-border
 * @param {string} backgroundColor - Bakgrundsfärg (default: tokens.colors.neutral.bg)
 */
export const ListItem = ({ 
  badge,
  badgeColor = 'green',
  title,
  description,
  metadata = [],
  actionButton,
  onClick,
  accentColor,
  backgroundColor
}) => {

  const getBadgeColor = (color) => {
    const colorMap = {
      'yellow': tokens.colors.ui.cardBgYellow,
      'blue': tokens.colors.ui.cardBgBlue,
      'green': tokens.colors.ui.cardBgGreen,
      'pink': tokens.colors.ui.cardBgPink,
      'orange': tokens.colors.ui.cardBgOrange
    };
    return colorMap[color?.toLowerCase()] || color || tokens.colors.ui.cardBgGreen;
  };

  const finalAccentColor = accentColor || tokens.colors.brand.secondary;
  // Always use white background for ListItems unless explicitly overridden, 
  // but even then, white is the preferred standard.
  const finalBackgroundColor = backgroundColor || tokens.colors.neutral.surface;

  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: finalBackgroundColor,
        padding: tokens.spacing['2xl'],
        borderRadius: '0', // ListItems have 0px radius by default standard
        boxShadow: tokens.shadows.card,
        border: 'none',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        marginBottom: tokens.spacing['2xl']
      }}
      onMouseEnter={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = tokens.shadows.card;
        }
      }}
    >
      {/* Badge */}
      {badge && (
        <div style={{ 
          display: 'flex', 
          alignItems: 'flex-start', 
          gap: tokens.spacing['2xl'], 
          marginBottom: tokens.spacing.lg 
        }}>
          <div style={{
            padding: `${tokens.spacing.xs} ${tokens.spacing.xl}`,
            backgroundColor: getBadgeColor(badgeColor),
            color: '#333',
            borderRadius: tokens.borderRadius.md, // Matchar kortens badge-rundning (8px)
            fontSize: '12px',
            fontWeight: 600,
            fontFamily: tokens.typography.fontFamily
          }}>
            {badge}
          </div>
        </div>
      )}

      {/* Title */}
      {title && (
        <h4 style={{ 
          fontSize: '18px', 
          fontWeight: 'bold', 
          marginBottom: tokens.spacing.md, 
          color: tokens.colors.neutral.text,
          fontFamily: tokens.typography.fontFamily
        }}>
          {title}
        </h4>
      )}

      {/* Description */}
      {description && (
        <p style={{ 
          fontSize: '14px', 
          color: '#666', 
          marginBottom: tokens.spacing['2xl'], 
          lineHeight: '1.6',
          fontFamily: tokens.typography.fontFamily
        }}>
          {description}
        </p>
      )}

      {/* Metadata */}
      {metadata && metadata.length > 0 && (
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: tokens.spacing['2xl'], 
          alignItems: 'center', 
          fontSize: '14px', 
          color: '#666', 
          marginBottom: tokens.spacing['2xl'],
          fontFamily: tokens.typography.fontFamily
        }}>
          {metadata.map((item, idx) => (
            <div 
              key={idx}
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: tokens.spacing.md 
              }}
            >
              {item.icon && <span style={{ display: 'flex', alignItems: 'center' }}>{item.icon}</span>}
              {item.text && <span>{item.text}</span>}
            </div>
          ))}
        </div>
      )}

      {/* Action Button */}
      {actionButton && (
        <div>
          {actionButton}
        </div>
      )}
    </div>
  );
};

ListItem.propTypes = {
  badge: PropTypes.string,
  badgeColor: PropTypes.string,
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  metadata: PropTypes.arrayOf(PropTypes.shape({
    icon: PropTypes.node,
    text: PropTypes.string
  })),
  actionButton: PropTypes.node,
  onClick: PropTypes.func,
  accentColor: PropTypes.string,
  backgroundColor: PropTypes.string
};

export default ListItem;

