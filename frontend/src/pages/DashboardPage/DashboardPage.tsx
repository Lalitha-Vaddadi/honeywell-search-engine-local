import { useState } from 'react';
import ThreePanelLayout from '@/components/layout/ThreePanelLayout';
import LeftPanelDocuments from '@/components/panels/LeftPanelDocuments';
import RightPanelSearchChat from '@/components/panels/RightPanelSearchChat';
import ViewerPage from '@/pages/ViewerPage';
import { Header } from '@/components/layout/Header';

export function DashboardPage() {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  return (
    <>
      <Header />

      <ThreePanelLayout
        left={
          <LeftPanelDocuments
            onSelectDocument={(id) => setSelectedDocument(id)}
          />
        }

        center={
          selectedDocument ? (
            <ViewerPage documentIdOverride={selectedDocument} />
          ) : (
            <div style={{ padding: 24 }}>
              <h2>Welcome</h2>
              <p>Select a PDF from the left or search from the right.</p>
            </div>
          )
        }

        right={
          <RightPanelSearchChat
            openDocument={(id, page) => {
              setSelectedDocument(id);
            }}
          />
        }
      />
    </>
  );
}
export default DashboardPage;
