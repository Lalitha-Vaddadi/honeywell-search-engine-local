// src/components/panels/CenterPanelViewer.tsx
import PdfJsViewer from "@/components/viewer/PdfJsViewer";

interface CenterPanelViewerProps {
  documentId?: string;
  pageNumber?: number;
}

export function CenterPanelViewer({
  documentId,
  pageNumber,
}: CenterPanelViewerProps) {
  if (!documentId) {
    return (
      <div
        style={{
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--panel-text-muted)",
        }}
      >
        Select a document to view
      </div>
    );
  }

  return (
    <PdfJsViewer
      documentId={documentId}
      page={pageNumber}
    />
  );
}
