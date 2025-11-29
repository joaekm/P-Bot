import React from 'react';
import { tokens } from '../tokens';

export const AddaInput = ({ 
  label, 
  type = 'text', 
  placeholder, 
  value, 
  onChange, 
  required = false,
  disabled = false,
  error,
  id,
  className = '',
  style = {},
  inputStyle: customInputStyle = {},
  ...props 
}) => {
  
  const containerStyle = {
    marginBottom: tokens.spacing['4xl'],
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    width: '100%',
    ...style
  };

  const labelStyle = {
    fontSize: tokens.typography.sizes.base,
    fontWeight: tokens.typography.weights.semibold,
    color: tokens.colors.neutral.text,
    marginBottom: tokens.spacing.md,
    fontFamily: tokens.typography.fontFamily,
  };

  const inputStyle = {
    width: '100%',
    padding: `${tokens.spacing.lg} ${tokens.spacing['2xl']}`,
    fontSize: tokens.typography.sizes.base,
    border: `1px solid ${error ? tokens.colors.brand.primary : tokens.colors.neutral.border}`,
    borderRadius: tokens.borderRadius.md,
    fontFamily: tokens.typography.fontFamily,
    outline: 'none',
    backgroundColor: disabled ? '#f5f5f5' : '#FFFFFF',
    color: tokens.colors.neutral.text,
    boxSizing: 'border-box',
    transition: 'border-color 0.2s ease',
    ...customInputStyle
  };

  const handleFocus = (e) => {
    if (!disabled && !error) {
      e.target.style.borderColor = tokens.colors.brand.secondary;
    }
  };

  const handleBlur = (e) => {
    if (!disabled && !error) {
      e.target.style.borderColor = tokens.colors.neutral.border;
    }
  };

  return (
    <div style={containerStyle} className={className}>
      {label && (
        <label htmlFor={id} style={labelStyle}>
          {label} {required && <span style={{ color: tokens.colors.brand.primary }}>*</span>}
        </label>
      )}
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        style={inputStyle}
        onFocus={handleFocus}
        onBlur={handleBlur}
        {...props}
      />
      {error && (
        <span style={{ 
          color: tokens.colors.brand.primary, 
          fontSize: tokens.typography.sizes.sm, 
          marginTop: tokens.spacing.xs,
          fontFamily: tokens.typography.fontFamily 
        }}>
          {error}
        </span>
      )}
    </div>
  );
};

export const AddaSelect = ({ 
    label, 
    options = [], 
    value, 
    onChange, 
    placeholder = 'Välj...', 
    required = false, 
    disabled = false,
    error,
    id,
    className = '',
    style = {},
    ...props 
  }) => {
    
    const containerStyle = {
        marginBottom: tokens.spacing['4xl'],
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-start',
        width: '100%',
        ...style
    };
  
    const labelStyle = {
        fontSize: tokens.typography.sizes.base,
        fontWeight: tokens.typography.weights.semibold,
        color: tokens.colors.neutral.text,
        marginBottom: tokens.spacing.md,
        fontFamily: tokens.typography.fontFamily,
    };
  
    const selectStyle = {
        width: '100%',
        padding: `${tokens.spacing.lg} ${tokens.spacing['2xl']}`,
        fontSize: tokens.typography.sizes.base,
        border: `1px solid ${error ? tokens.colors.brand.primary : tokens.colors.neutral.border}`,
        borderRadius: tokens.borderRadius.md,
        fontFamily: tokens.typography.fontFamily,
        outline: 'none',
        backgroundColor: disabled ? '#f5f5f5' : '#FFFFFF',
        color: tokens.colors.neutral.text,
        boxSizing: 'border-box',
        cursor: disabled ? 'not-allowed' : 'pointer',
        appearance: 'none', // Remove default arrow
        backgroundImage: `url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23005B59%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4l128-128c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 1rem center',
        backgroundSize: '.65em auto',
    };

    const handleFocus = (e) => {
        if (!disabled && !error) {
          e.target.style.borderColor = tokens.colors.brand.secondary;
        }
      };
    
      const handleBlur = (e) => {
        if (!disabled && !error) {
          e.target.style.borderColor = tokens.colors.neutral.border;
        }
      };
  
    return (
      <div style={containerStyle} className={className}>
        {label && (
          <label htmlFor={id} style={labelStyle}>
            {label} {required && <span style={{ color: tokens.colors.brand.primary }}>*</span>}
          </label>
        )}
        <select
          id={id}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          style={selectStyle}
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...props}
        >
          <option value="" disabled>{placeholder}</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {error && (
            <span style={{ 
              color: tokens.colors.brand.primary, 
              fontSize: tokens.typography.sizes.sm, 
              marginTop: tokens.spacing.xs,
              fontFamily: tokens.typography.fontFamily 
            }}>
              {error}
            </span>
          )}
      </div>
    );
  };

  export const AddaTextarea = ({ 
    label, 
    placeholder, 
    value, 
    onChange, 
    required = false,
    disabled = false,
    rows = 4,
    error,
    id,
    className = '',
    style = {},
    ...props 
  }) => {
    
    const containerStyle = {
      marginBottom: tokens.spacing['4xl'],
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      width: '100%',
      ...style
    };
  
    const labelStyle = {
      fontSize: tokens.typography.sizes.base,
      fontWeight: tokens.typography.weights.semibold,
      color: tokens.colors.neutral.text,
      marginBottom: tokens.spacing.md,
      fontFamily: tokens.typography.fontFamily,
    };
  
    const inputStyle = {
      width: '100%',
      padding: `${tokens.spacing.lg} ${tokens.spacing['2xl']}`,
      fontSize: tokens.typography.sizes.base,
      border: `1px solid ${error ? tokens.colors.brand.primary : tokens.colors.neutral.border}`,
      borderRadius: tokens.borderRadius.md,
      fontFamily: tokens.typography.fontFamily,
      outline: 'none',
      backgroundColor: disabled ? '#f5f5f5' : '#FFFFFF',
      color: tokens.colors.neutral.text,
      boxSizing: 'border-box',
      transition: 'border-color 0.2s ease',
      resize: 'vertical',
    };
  
    const handleFocus = (e) => {
      if (!disabled && !error) {
        e.target.style.borderColor = tokens.colors.brand.secondary;
      }
    };
  
    const handleBlur = (e) => {
      if (!disabled && !error) {
        e.target.style.borderColor = tokens.colors.neutral.border;
      }
    };
  
    return (
      <div style={containerStyle} className={className}>
        {label && (
          <label htmlFor={id} style={labelStyle}>
            {label} {required && <span style={{ color: tokens.colors.brand.primary }}>*</span>}
          </label>
        )}
        <textarea
          id={id}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          rows={rows}
          style={inputStyle}
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...props}
        />
        {error && (
          <span style={{ 
            color: tokens.colors.brand.primary, 
            fontSize: tokens.typography.sizes.sm, 
            marginTop: tokens.spacing.xs,
            fontFamily: tokens.typography.fontFamily 
          }}>
            {error}
          </span>
        )}
      </div>
    );
  };

