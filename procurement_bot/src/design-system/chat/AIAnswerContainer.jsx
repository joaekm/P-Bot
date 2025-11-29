import React from 'react';
import PropTypes from 'prop-types';
import ReactMarkdown from 'react-markdown';
import { tokens } from '../tokens';
import { ChatAvatar } from './ChatAvatar';

/**
 * AIAnswerContainer - Pratbubbla för AI-svar, vänsterställd
 * 
 * Supports Markdown rendering for rich text formatting.
 * 
 * @param {string} text - Text content to display (supports Markdown)
 * @param {string} avatar - Avatar image URL
 * @param {node} children - Additional content
 * @param {object} style - Additional styles
 */
export const AIAnswerContainer = ({ 
  text, 
  avatar,
  children,
  style = {} 
}) => {
  // Custom styles for Markdown elements
  const markdownStyles = {
    container: {
      fontFamily: tokens.typography.fontFamily,
      fontSize: tokens.typography.sizes.base,
      lineHeight: tokens.typography.lineHeights.relaxed,
      color: tokens.colors.neutral.text,
    },
    p: {
      marginBottom: tokens.spacing.md,
      marginTop: 0,
    },
    ul: {
      marginBottom: tokens.spacing.md,
      paddingLeft: tokens.spacing.xl,
    },
    ol: {
      marginBottom: tokens.spacing.md,
      paddingLeft: tokens.spacing.xl,
    },
    li: {
      marginBottom: tokens.spacing.xs,
    },
    strong: {
      fontWeight: tokens.typography.weights.bold,
    },
    h1: {
      fontSize: tokens.typography.sizes.xl,
      fontWeight: tokens.typography.weights.bold,
      marginBottom: tokens.spacing.md,
      marginTop: tokens.spacing.lg,
    },
    h2: {
      fontSize: tokens.typography.sizes.lg,
      fontWeight: tokens.typography.weights.bold,
      marginBottom: tokens.spacing.sm,
      marginTop: tokens.spacing.md,
    },
    h3: {
      fontSize: tokens.typography.sizes.md,
      fontWeight: tokens.typography.weights.semibold,
      marginBottom: tokens.spacing.sm,
      marginTop: tokens.spacing.md,
    },
    code: {
      backgroundColor: tokens.colors.neutral.bg,
      padding: '2px 6px',
      borderRadius: tokens.borderRadius.sm,
      fontFamily: 'monospace',
      fontSize: '0.9em',
    },
    hr: {
      border: 'none',
      borderTop: `1px solid ${tokens.colors.neutral.border}`,
      margin: `${tokens.spacing.lg} 0`,
    },
  };

  return (
    <div 
      style={{
        display: 'flex',
        justifyContent: 'flex-start',
        marginBottom: tokens.spacing['4xl'],
        paddingLeft: tokens.spacing['4xl'],
        paddingRight: tokens.spacing['4xl'],
        maxWidth: tokens.layout.containerMaxWidth,
        ...style
      }}
    >
      <div style={{ display: 'flex', gap: tokens.spacing['2xl'], alignItems: 'flex-start', maxWidth: '85%' }}>
        {avatar && <ChatAvatar src={avatar} alt="AI Assistant" size={40} />}
        
        <div 
          style={{
            backgroundColor: tokens.colors.ui.cardBgBlue,
            padding: tokens.spacing['4xl'],
            borderRadius: tokens.borderRadius.lg,
            flex: 1,
          }}
        >
          <div style={markdownStyles.container} className="ai-markdown-content">
            <ReactMarkdown
              components={{
                p: ({ children }) => <p style={markdownStyles.p}>{children}</p>,
                ul: ({ children }) => <ul style={markdownStyles.ul}>{children}</ul>,
                ol: ({ children }) => <ol style={markdownStyles.ol}>{children}</ol>,
                li: ({ children }) => <li style={markdownStyles.li}>{children}</li>,
                strong: ({ children }) => <strong style={markdownStyles.strong}>{children}</strong>,
                h1: ({ children }) => <h1 style={markdownStyles.h1}>{children}</h1>,
                h2: ({ children }) => <h2 style={markdownStyles.h2}>{children}</h2>,
                h3: ({ children }) => <h3 style={markdownStyles.h3}>{children}</h3>,
                code: ({ children }) => <code style={markdownStyles.code}>{children}</code>,
                hr: () => <hr style={markdownStyles.hr} />,
              }}
            >
              {text}
            </ReactMarkdown>
          </div>
          
          {children && (
            <div style={{ marginTop: tokens.spacing['2xl'] }}>
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

AIAnswerContainer.propTypes = {
  text: PropTypes.string.isRequired,
  avatar: PropTypes.string,
  children: PropTypes.node,
  style: PropTypes.object
};

export default AIAnswerContainer;


