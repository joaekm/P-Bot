import React from 'react';
import { tokens } from '../tokens';

/**
 * PageTitle - Standardiserad sidtitel för alla vyer
 * Används konsekvent i alla layout-typer (Landing, FullWidth, Sidebar)
 */
export const PageTitle = ({ children, style = {} }) => {
  return (
    <h1 
      style={{ 
        fontSize: '32px', 
        fontWeight: 'bold', 
        marginBottom: '24px',
        color: tokens.colors.neutral.text,
        lineHeight: 1.2,
        ...style
      }}
    >
      {children}
    </h1>
  );
};

export default PageTitle;



