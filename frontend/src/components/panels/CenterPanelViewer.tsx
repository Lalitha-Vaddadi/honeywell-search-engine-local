// src/components/panels/CenterPanelViewer.tsx
import React, { useState } from 'react';
import ViewerPage from '@/pages/ViewerPage';

interface CenterPanelViewerProps {
  documentId?: string;
  pageNumber?: number;
}

export function CenterPanelViewer({ 
  documentId, 
  pageNumber 
}: CenterPanelViewerProps) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | undefined>(documentId);
  const [selectedPageNumber, setSelectedPageNumber] = useState<number | undefined>(pageNumber);

  return (
    <div style={{ height: '100%', width: '100%', position: 'relative' }}>
      {selectedDocumentId ? (
        <ViewerPage 
          documentIdOverride={selectedDocumentId}
          pageOverride={selectedPageNumber}
        />
      ) : (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          backgroundColor: '#f8f9fa',
          color: '#6c757d',
          fontSize: '14px'
        }}>
          Select a document to view
        </div>
      )}
    </div>
  );
}
