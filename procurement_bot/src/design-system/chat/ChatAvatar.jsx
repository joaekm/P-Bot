import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';

/**
 * ChatAvatar - Avatar component for chat messages
 * 
 * @param {string} src - Image source URL
 * @param {string} alt - Alt text for the image
 * @param {number} size - Avatar size in pixels (default: 40)
 */
export const ChatAvatar = ({ src, alt = 'Avatar', size = 40 }) => {
  return (
    <img 
      src={src} 
      alt={alt} 
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: '50%',
        flexShrink: 0,
        objectFit: 'cover',
        border: `2px solid ${tokens.colors.neutral.border}`
      }}
    />
  );
};

ChatAvatar.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string,
  size: PropTypes.number
};

export default ChatAvatar;

