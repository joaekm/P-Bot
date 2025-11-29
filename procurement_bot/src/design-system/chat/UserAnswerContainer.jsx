import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { BodyText } from '../components/AddaTypography';
import { ChatAvatar } from './ChatAvatar';

/**
 * UserAnswerContainer - Pratbubbla för användarsvar, högerställd
 * 
 * @param {string} text - Text content to display
 * @param {string} avatar - Avatar image URL (optional)
 * @param {node} children - Additional content
 * @param {object} style - Additional styles
 */
export const UserAnswerContainer = ({ 
  text, 
  avatar,
  children,
  style = {} 
}) => {
  return (
    <div 
      style={{
        display: 'flex',
        justifyContent: 'flex-end',
        marginBottom: tokens.spacing['4xl'],
        paddingLeft: tokens.spacing['4xl'],
        paddingRight: tokens.spacing['4xl'],
        maxWidth: tokens.layout.containerMaxWidth,
        ...style
      }}
    >
      <div style={{ display: 'flex', gap: tokens.spacing['2xl'], alignItems: 'flex-start', maxWidth: '85%', flexDirection: 'row-reverse' }}>
        {avatar && <ChatAvatar src={avatar} alt="User" size={40} />}
        
        <div 
          style={{
            backgroundColor: tokens.colors.ui.cardBgYellow,
            padding: tokens.spacing['4xl'],
            borderRadius: tokens.borderRadius.lg,
            flex: 1,
          }}
        >
          <BodyText style={{ marginBottom: 0, marginTop: 0 }}>
            {text}
          </BodyText>
          
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

UserAnswerContainer.propTypes = {
  text: PropTypes.string.isRequired,
  avatar: PropTypes.string,
  children: PropTypes.node,
  style: PropTypes.object
};

export default UserAnswerContainer;


