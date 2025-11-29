import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Users, MapPin, Briefcase } from 'lucide-react';

/**
 * ResourceSummaryCard Component
 * 
 * Displays a summary of extracted resources from document analysis
 * or user input. Used as a stream_widget in the chat.
 */
const ResourceSummaryCard = ({ 
  resources = [], 
  title = 'Identifierade resurser',
  showConfidence = false,
  confidence = null 
}) => {
  if (!resources || resources.length === 0) {
    return (
      <div
        style={{
          backgroundColor: tokens.colors.ui.cardBgYellow,
          borderRadius: tokens.borderRadius.lg,
          padding: tokens.spacing.xl,
          marginTop: tokens.spacing.md,
          marginBottom: tokens.spacing.md,
          fontFamily: tokens.typography.fontFamily,
          textAlign: 'center',
          color: tokens.colors.neutral.lightGrey,
        }}
      >
        Inga resurser identifierade
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: tokens.colors.ui.cardBgBlue,
        borderRadius: tokens.borderRadius.lg,
        padding: tokens.spacing.xl,
        marginTop: tokens.spacing.md,
        marginBottom: tokens.spacing.md,
        fontFamily: tokens.typography.fontFamily,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: tokens.spacing.lg,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: tokens.spacing.sm,
          }}
        >
          <Briefcase size={20} color={tokens.colors.brand.secondary} />
          <span
            style={{
              fontWeight: tokens.typography.weights.bold,
              color: tokens.colors.neutral.text,
              fontSize: tokens.typography.sizes.md,
            }}
          >
            {title}
          </span>
        </div>
        
        {showConfidence && confidence && (
          <span
            style={{
              fontSize: tokens.typography.sizes.xs,
              padding: `${tokens.spacing.xs} ${tokens.spacing.sm}`,
              borderRadius: tokens.borderRadius.pill,
              backgroundColor: confidence === 'high' 
                ? tokens.colors.status.successBg 
                : confidence === 'medium'
                ? tokens.colors.status.warningBg
                : tokens.colors.status.errorBg,
              color: confidence === 'high'
                ? tokens.colors.status.successDark
                : confidence === 'medium'
                ? tokens.colors.status.warningDark
                : tokens.colors.status.errorDark,
            }}
          >
            {confidence === 'high' ? 'Hög' : confidence === 'medium' ? 'Medium' : 'Låg'} konfidens
          </span>
        )}
      </div>

      {/* Resource List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing.sm }}>
        {resources.map((resource, index) => (
          <div
            key={index}
            style={{
              backgroundColor: tokens.colors.neutral.surface,
              borderRadius: tokens.borderRadius.md,
              padding: tokens.spacing.md,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing.md }}>
              <div
                style={{
                  backgroundColor: tokens.colors.brand.lightTint,
                  borderRadius: tokens.borderRadius.iconCircle,
                  width: '36px',
                  height: '36px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Users size={18} color={tokens.colors.brand.secondary} />
              </div>
              
              <div>
                <div
                  style={{
                    fontWeight: tokens.typography.weights.semibold,
                    color: tokens.colors.neutral.text,
                    fontSize: tokens.typography.sizes.md,
                  }}
                >
                  {resource.quantity > 1 ? `${resource.quantity}x ` : ''}{resource.role}
                </div>
                
                {resource.location && (
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: tokens.spacing.xs,
                      fontSize: tokens.typography.sizes.sm,
                      color: tokens.colors.neutral.lightGrey,
                      marginTop: tokens.spacing.xs,
                    }}
                  >
                    <MapPin size={14} />
                    {resource.location}
                  </div>
                )}
              </div>
            </div>
            
            {resource.level && (
              <span
                style={{
                  fontSize: tokens.typography.sizes.sm,
                  padding: `${tokens.spacing.xs} ${tokens.spacing.md}`,
                  borderRadius: tokens.borderRadius.pill,
                  backgroundColor: tokens.colors.brand.lightTint,
                  color: tokens.colors.brand.secondary,
                  fontWeight: tokens.typography.weights.semibold,
                }}
              >
                Nivå {resource.level}
              </span>
            )}
          </div>
        ))}
      </div>
      
      {/* Summary */}
      <div
        style={{
          marginTop: tokens.spacing.lg,
          paddingTop: tokens.spacing.md,
          borderTop: `1px solid ${tokens.colors.neutral.border}`,
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: tokens.typography.sizes.sm,
          color: tokens.colors.neutral.lightGrey,
        }}
      >
        <span>Totalt: {resources.length} {resources.length === 1 ? 'resurs' : 'resurser'}</span>
        <span>
          {resources.reduce((sum, r) => sum + (r.quantity || 1), 0)} personer
        </span>
      </div>
    </div>
  );
};

ResourceSummaryCard.propTypes = {
  resources: PropTypes.arrayOf(PropTypes.shape({
    role: PropTypes.string.isRequired,
    quantity: PropTypes.number,
    location: PropTypes.string,
    level: PropTypes.number,
  })),
  title: PropTypes.string,
  showConfidence: PropTypes.bool,
  confidence: PropTypes.oneOf(['high', 'medium', 'low']),
};

export default ResourceSummaryCard;



