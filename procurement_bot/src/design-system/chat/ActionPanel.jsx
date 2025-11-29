import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { AddaButton } from '../components/AddaButton';
import { AddaInput } from '../components/AddaInput';
import { Send, UploadCloud, Loader, ArrowUp } from 'lucide-react';

/**
 * ActionPanel Component
 * 
 * Server-driven input zone for the chat interface.
 * Supports multiple modes controlled by the backend:
 * - text_input: Free text input with send button
 * - binary_choice: Only action buttons, no text input
 * - file_upload: File upload button
 * - locked: Disabled state (processing)
 * 
 * @example
 * // Text input mode
 * <ActionPanel 
 *   mode="text_input"
 *   placeholder="Skriv ditt meddelande..."
 *   onTextSubmit={(text) => console.log(text)}
 * />
 * 
 * @example
 * // Binary choice mode
 * <ActionPanel 
 *   mode="binary_choice"
 *   actions={[{ label: 'Ja', value: 'yes' }, { label: 'Nej', value: 'no' }]}
 *   onActionClick={(value) => console.log(value)}
 * />
 */
const ActionPanel = ({
  mode = 'text_input',
  placeholder = 'Skriv här...',
  actions = [],
  onTextSubmit,
  onActionClick,
  onFileUpload,
  disabled = false,
  isLoading = false,
  style = {}
}) => {
  const [message, setMessage] = useState('');
  const fileInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled && onTextSubmit) {
      onTextSubmit(message);
      setMessage('');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file);
      e.target.value = '';
    }
  };

  const isLocked = mode === 'locked' || disabled || isLoading;

  return (
    <div
      style={{
        padding: tokens.spacing['2xl'],
        borderTop: `1px solid ${tokens.colors.neutral.border}`,
        backgroundColor: tokens.colors.neutral.surface,
        flexShrink: 0, // Don't shrink in flex container
        ...style
      }}
    >
      {/* Text Input Mode */}
      {(mode === 'text_input' || mode === 'file_upload') && (
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: tokens.spacing.md }}>
          <AddaInput
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={isLocked}
            placeholder={placeholder || 'Skriv här...'}
            style={{ flex: 1, marginBottom: 0 }}
            inputStyle={{ borderRadius: '16px' }}
          />
          <AddaButton 
            type="submit" 
            variant="sendButton"
            disabled={!message.trim() || isLocked}
          >
            {isLoading ? (
              <Loader size={20} className="animate-spin" color={tokens.colors.brand.lightTint} />
            ) : (
              <ArrowUp size={24} color={tokens.colors.brand.lightTint} /> // Ice Teal
            )}
          </AddaButton>
        </form>
      )}

      {/* Binary Choice Mode - Only buttons */}
      {mode === 'binary_choice' && actions.length > 0 && (
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: tokens.spacing.md,
            justifyContent: 'center'
          }}
        >
          {actions.map((action, index) => (
            <AddaButton
              key={action.value || index}
              variant={index === 0 ? 'primary' : 'secondary'}
              onClick={() => onActionClick && onActionClick(action.value)}
              disabled={isLocked}
            >
              {action.label}
            </AddaButton>
          ))}
        </div>
      )}

      {/* File Upload Button */}
      {(mode === 'file_upload' || mode === 'text_input') && onFileUpload && (
        <div style={{ marginTop: tokens.spacing.lg, textAlign: 'center' }}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{ display: 'none' }}
            accept=".pdf,.docx,.doc,.xlsx,.xls,.txt,.md"
          />
          <AddaButton
            variant="secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLocked}
            style={{ display: 'inline-flex', alignItems: 'center', gap: tokens.spacing.sm }}
          >
            <UploadCloud size={18} /> Ladda upp underlag
          </AddaButton>
        </div>
      )}

      {/* Locked Mode - Show loading indicator */}
      {mode === 'locked' && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: tokens.spacing.md,
            padding: tokens.spacing.lg,
            color: tokens.colors.neutral.lightGrey,
            fontFamily: tokens.typography.fontFamily,
            fontSize: tokens.typography.sizes.sm
          }}
        >
          <Loader size={20} className="animate-spin" />
          <span>Bearbetar...</span>
        </div>
      )}
    </div>
  );
};

ActionPanel.propTypes = {
  mode: PropTypes.oneOf(['text_input', 'binary_choice', 'file_upload', 'locked']),
  placeholder: PropTypes.string,
  actions: PropTypes.arrayOf(PropTypes.shape({
    label: PropTypes.string.isRequired,
    value: PropTypes.string.isRequired
  })),
  onTextSubmit: PropTypes.func,
  onActionClick: PropTypes.func,
  onFileUpload: PropTypes.func,
  disabled: PropTypes.bool,
  isLoading: PropTypes.bool,
  style: PropTypes.object
};

export default ActionPanel;

