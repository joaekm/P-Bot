import React from 'react';
import { tokens } from '../tokens';

export const AddaButton = ({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  onClick, 
  disabled = false,
  className = '',
  style = {},
  ...props 
}) => {
  
  const baseStyle = {
    borderRadius: tokens.borderRadius.pill,
    fontWeight: tokens.typography.weights.bold,
    fontSize: size === 'small' ? tokens.typography.sizes.sm : tokens.typography.sizes.base,
    padding: size === 'small' ? `${tokens.spacing.md} ${tokens.spacing.xl}` : `${tokens.spacing.xl} ${tokens.spacing['4xl']}`,
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease',
    border: 'none',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: tokens.spacing.md,
    fontFamily: tokens.typography.fontFamily,
    opacity: disabled ? 0.6 : 1,
    ...style
  };

  const variants = {
    primary: {
      backgroundColor: tokens.colors.brand.primary,
      color: '#FFFFFF',
      boxShadow: disabled ? 'none' : tokens.shadows.button,
      border: `2px solid ${tokens.colors.brand.primary}`,
    },
    secondary: {
      backgroundColor: tokens.colors.neutral.surface,
      color: tokens.colors.brand.secondary,
      border: `2px solid ${tokens.colors.brand.secondary}`,
    },
    outline: {
      backgroundColor: 'transparent',
      color: '#FFFFFF',
      border: '1px solid #FFFFFF',
    },
    text: {
      backgroundColor: 'transparent',
      color: tokens.colors.brand.primary,
      border: 'none',
      padding: 0,
      boxShadow: 'none',
    },
    selected: {
      backgroundColor: tokens.colors.ui.iconBg,
      color: tokens.colors.brand.secondary,
      border: `2px solid ${tokens.colors.brand.secondary}`,
    },
    sendButton: {
      backgroundColor: tokens.colors.brand.secondary, // Dark Petrol
      color: tokens.colors.brand.lightTint, // Ice Teal
      border: 'none',
      boxShadow: disabled ? 'none' : '0 4px 12px rgba(0, 91, 89, 0.3)', // Petrol shadow
      borderRadius: '50%',
      width: '40px',
      height: '40px',
      padding: 0,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0
    }
  };

  // Hover effects handling (simple implementation using onMouseEnter/onMouseLeave)
  const handleMouseEnter = (e) => {
    if (disabled) return;
    
    if (variant === 'primary') {
      e.currentTarget.style.transform = 'translateY(-2px)';
      e.currentTarget.style.boxShadow = '0 6px 16px rgba(211, 47, 0, 0.4)';
    } else if (variant === 'secondary') {
      e.currentTarget.style.backgroundColor = tokens.colors.brand.secondary;
      e.currentTarget.style.color = '#FFFFFF';
    } else if (variant === 'outline') {
      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.1)';
    } else if (variant === 'text') {
      e.currentTarget.style.textDecoration = 'underline';
    } else if (variant === 'sendButton') {
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = '0 6px 16px rgba(0, 91, 89, 0.5)'; // Stronger petrol shadow
    }
    // 'selected' variant usually doesn't have a distinct hover state other than standard button behavior or handled elsewhere
  };

  const handleMouseLeave = (e) => {
    if (disabled) return;
    
    if (variant === 'primary') {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.boxShadow = tokens.shadows.button;
    } else if (variant === 'secondary') {
      e.currentTarget.style.backgroundColor = tokens.colors.neutral.surface;
      e.currentTarget.style.color = tokens.colors.brand.secondary;
    } else if (variant === 'outline') {
      e.currentTarget.style.backgroundColor = 'transparent';
    } else if (variant === 'text') {
      e.currentTarget.style.textDecoration = 'none';
    } else if (variant === 'sendButton') {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 91, 89, 0.3)';
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ ...baseStyle, ...variants[variant], ...style }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={className}
      {...props}
    >
      {children}
    </button>
  );
};
