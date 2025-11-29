import React from 'react';
import { tokens } from '../tokens';

const LayoutSidebarLeft = ({ children, sidebar, title }) => {
  return (
    <div className="adda-container-system" style={{ paddingTop: '32px', paddingBottom: '32px' }}>
      {title && (
         <div style={{ marginBottom: '24px', width: '100%' }}>
          {title}
        </div>
      )}
      <div className="adda-layout-grid">
        <aside className="adda-col-sidebar">
          {sidebar}
        </aside>
        <div className="adda-col-main">
          {children}
        </div>
      </div>
    </div>
  );
};

export default LayoutSidebarLeft;
