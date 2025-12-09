import React, { useRef, useEffect } from 'react';
import { tokens } from '../tokens';

/**
 * ChatInput - Auto-expanding textarea for chat
 * Grows upward as user types, no manual resize
 * Enter sends message, Shift+Enter for new line
 */
const ChatInput = ({
  value,
  onChange,
  onSubmit,
  placeholder = 'Skriv här...',
  disabled = false,
  maxHeight = 200,
  style = {}
}) => {
  const textareaRef = useRef(null);

  // Auto-resize on value change
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
    }
  }, [value, maxHeight]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && onSubmit) {
        onSubmit(value);
      }
    }
  };

  const handleFocus = (e) => {
    if (!disabled) {
      e.target.style.borderColor = tokens.colors.brand.secondary;
    }
  };

  const handleBlur = (e) => {
    if (!disabled) {
      e.target.style.borderColor = tokens.colors.neutral.border;
    }
  };

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={onChange}
      onKeyDown={handleKeyDown}
      onFocus={handleFocus}
      onBlur={handleBlur}
      disabled={disabled}
      placeholder={placeholder}
      rows={1}
      style={{
        width: '100%',
        padding: `${tokens.spacing.lg} ${tokens.spacing['2xl']}`,
        fontSize: tokens.typography.sizes.base,
        fontFamily: tokens.typography.fontFamily,
        border: `1px solid ${tokens.colors.neutral.border}`,
        borderRadius: '16px',
        outline: 'none',
        backgroundColor: disabled ? '#f5f5f5' : '#FFFFFF',
        color: tokens.colors.neutral.text,
        boxSizing: 'border-box',
        resize: 'none',
        overflow: 'hidden',
        minHeight: '44px',
        maxHeight: `${maxHeight}px`,
        lineHeight: '1.4',
        transition: 'border-color 0.2s ease',
        ...style
      }}
    />
  );
};

export default ChatInput;

