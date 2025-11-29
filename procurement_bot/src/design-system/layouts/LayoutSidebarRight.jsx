import React from 'react';
import { tokens } from '../tokens';

const LayoutSidebarRight = ({ children, sidebar, title }) => {
  return (
    <div className="adda-container-system" style={{ paddingTop: '32px', paddingBottom: '32px' }}>
      {title && (
        <div style={{ marginBottom: '24px', width: '100%' }}>
          {title}
        </div>
      )}
      <div className="adda-layout-grid">
        <div className="adda-col-main">
          {children}
        </div>
        <aside className="adda-col-sidebar">
          {sidebar}
        </aside>
      </div>
    </div>
  );
};

export default LayoutSidebarRight;
