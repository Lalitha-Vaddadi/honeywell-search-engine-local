import { useState } from "react"
import ThreePanelLayout from "@/components/layout/ThreePanelLayout"
import LeftPanelDocuments from "@/components/panels/LeftPanelDocuments"
import { RightPanelSearchChat } from "@/components/panels/RightPanelSearchChat"
import { Header } from "@/components/layout/Header"
import PdfJsViewer from "@/components/viewer/PdfJsViewer"

export function DashboardPage() {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null)
  const [pageOverride, setPageOverride] = useState<number | undefined>(undefined)
  const [highlightText, setHighlightText] = useState<string | null>(null)

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <Header />

      <div style={{ flex: 1, minHeight: 0 }}>
        <ThreePanelLayout
          left={
            <LeftPanelDocuments
              onSelectDocument={(id) => {
                setSelectedDocument(id)
                setPageOverride(undefined)
                setHighlightText(null)
              }}
            />
          }
          center={
            selectedDocument ? (
              <PdfJsViewer
                documentId={selectedDocument}
                page={pageOverride}
                highlightText={highlightText}
              />
            ) : (
              <div
                style={{
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "var(--panel-text-muted)",
                }}
              >
                Select a PDF from the left
              </div>
            )
          }
          right={
            <RightPanelSearchChat
              onOpenResult={(docId, page, highlight) => {
                setSelectedDocument(docId)
                setPageOverride(page)
                setHighlightText(highlight)
              }}
            />
          }
        />
      </div>
    </div>
  )
}

export default DashboardPage