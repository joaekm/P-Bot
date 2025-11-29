import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Bug } from 'lucide-react';

/**
 * DebugCard Component
 * 
 * A simple debug/test widget for verifying server-driven UI.
 * Displays any props passed from the backend.
 */
const DebugCard = ({ title = 'Debug Widget', data = {}, ...props }) => {
  return (
    <div
      style={{
        backgroundColor: '#FEF3C7', // Amber-100
        border: '2px dashed #F59E0B', // Amber-500
        borderRadius: tokens.borderRadius.lg,
        padding: tokens.spacing.xl,
        marginTop: tokens.spacing.md,
        marginBottom: tokens.spacing.md,
        fontFamily: tokens.typography.fontFamily,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: tokens.spacing.sm,
          marginBottom: tokens.spacing.md,
        }}
      >
        <Bug size={20} color="#D97706" />
        <span
          style={{
            fontWeight: tokens.typography.weights.bold,
            color: '#92400E', // Amber-800
            fontSize: tokens.typography.sizes.md,
          }}
        >
          {title}
        </span>
      </div>
      
      <div
        style={{
          backgroundColor: 'rgba(255,255,255,0.7)',
          borderRadius: tokens.borderRadius.md,
          padding: tokens.spacing.md,
          fontSize: tokens.typography.sizes.sm,
          fontFamily: 'monospace',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}
      >
        {JSON.stringify(data, null, 2) || '(No data)'}
      </div>
      
      {Object.keys(props).length > 0 && (
        <div
          style={{
            marginTop: tokens.spacing.md,
            fontSize: tokens.typography.sizes.xs,
            color: '#92400E',
          }}
        >
          Additional props: {Object.keys(props).join(', ')}
        </div>
      )}
    </div>
  );
};

DebugCard.propTypes = {
  title: PropTypes.string,
  data: PropTypes.object,
};

export default DebugCard;



