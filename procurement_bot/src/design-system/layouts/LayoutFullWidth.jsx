import React from 'react';
import { tokens } from '../tokens';

const LayoutFullWidth = ({ children }) => {
  return (
    <div className="adda-container-system" style={{ paddingTop: tokens.spacing['4xl'], paddingBottom: tokens.spacing['4xl'] }}>
      {children}
    </div>
  );
};

export default LayoutFullWidth;

