import { useEffect, useRef, useState } from "react"
import * as pdfjsLib from "pdfjs-dist"
import workerSrc from "pdfjs-dist/build/pdf.worker.mjs?url"
import { documentsApi } from "@/api"

pdfjsLib.GlobalWorkerOptions.workerSrc = workerSrc

interface HighlightBox {
  x: number
  y: number
  width: number
  height: number
}

interface Props {
  documentId: string
  page?: number
  highlightText?: string | null
}

const normalize = (t: string) =>
  t
    .toLowerCase()
    .replace(/[^\w\s]/g, "")
    .replace(/\s+/g, " ")
    .trim()

export default function PdfJsViewer({
  documentId,
  page = 1,
  highlightText,
}: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const [pdfDoc, setPdfDoc] = useState<pdfjsLib.PDFDocumentProxy | null>(null)
  const [currentPage, setCurrentPage] = useState(page)
  const [numPages, setNumPages] = useState(0)
  const [docName, setDocName] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [highlights, setHighlights] = useState<HighlightBox[]>([])

  /* -------- Load PDF -------- */
  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        const meta = await documentsApi.getDocument(documentId)
        if (!cancelled) setDocName(meta.data.filename)

        const blob = await documentsApi.getDocumentFile(documentId)
        const buffer = await blob.arrayBuffer()

        const pdf = await pdfjsLib.getDocument({ data: buffer }).promise
        if (cancelled) return

        setPdfDoc(pdf)
        setNumPages(pdf.numPages)
        setCurrentPage(page)
        setHighlights([])
      } catch {
        if (!cancelled) setError("Failed to load PDF")
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [documentId])

  /* -------- Sync page from search -------- */
  useEffect(() => {
    if (typeof page === "number") {
      setCurrentPage(page)
      setHighlights([])
    }
  }, [page])

  /* -------- Render page + compute highlights -------- */
  useEffect(() => {
    if (!pdfDoc || !scrollRef.current) return

    let cancelled = false

    const render = async () => {
      const canvas = canvasRef.current
      const container = scrollRef.current
      if (!canvas || !container) return

      const pageObj = await pdfDoc.getPage(currentPage)
      if (cancelled) return

      const baseViewport = pageObj.getViewport({ scale: 1 })
      const scale = (container.clientWidth - 32) / baseViewport.width
      const viewport = pageObj.getViewport({ scale })

      canvas.width = viewport.width
      canvas.height = viewport.height

      const ctx = canvas.getContext("2d")
      if (!ctx) return

      ctx.setTransform(1, 0, 0, 1, 0, 0)
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      await pageObj.render({
        canvasContext: ctx,
        viewport,
      }).promise

      if (!highlightText) {
        setHighlights([])
        return
      }

      const textContent = await pageObj.getTextContent()
      const items = textContent.items as any[]

      const normalizedTarget = normalize(highlightText)
      const normalizedItems = items.map(it => normalize(it.str))

      let matchStart = -1
      let matchEnd = -1

      for (let i = 0; i < normalizedItems.length; i++) {
        let windowText = ""
        for (
          let j = i;
          j < normalizedItems.length &&
          windowText.length < normalizedTarget.length + 20;
          j++
        ) {
          windowText += normalizedItems[j] + " "
          if (windowText.includes(normalizedTarget)) {
            matchStart = i
            matchEnd = j
            break
          }
        }
        if (matchStart !== -1) break
      }

      if (matchStart === -1) {
        setHighlights([])
        return
      }

      const boxes: HighlightBox[] = []

      for (let i = matchStart; i <= matchEnd; i++) {
        const item = items[i]
        const [, , , , x, y] = item.transform

        const [vx, vy] = viewport.convertToViewportPoint(x, y)

        const height =
          item.height
            ? item.height * scale
            : Math.abs(item.transform[3]) * scale

        const width = item.width * scale

        boxes.push({
          x: vx,
          y: vy - height,
          width,
          height,
        })
      }

      setHighlights(boxes)
    }

    render()
    return () => {
      cancelled = true
    }
  }, [pdfDoc, currentPage, highlightText])

  if (error) {
    return <div style={{ padding: 24, color: "var(--danger)" }}>{error}</div>
  }

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* -------- HEADER -------- */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "12px 16px",
          borderBottom: "1px solid var(--pdf-controls-border)",
          background: "var(--panel-bg)",
          flexShrink: 0,
        }}
      >
        <div
          title={docName}
          style={{
            fontWeight: 600,
            fontSize: 14,
            maxWidth: "60%",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
            color: "var(--panel-text-primary)",
          }}
        >
          {docName}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage <= 1}
            style={btn}
          >
            Prev
          </button>

          <span style={{ fontSize: 13, color: "var(--panel-text-muted)" }}>
            Page {currentPage} of {numPages}
          </span>

          <button
            onClick={() => setCurrentPage(p => Math.min(numPages, p + 1))}
            disabled={currentPage >= numPages}
            style={btn}
          >
            Next
          </button>
        </div>
      </div>

      {/* -------- BODY -------- */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflow: "auto",
          padding: 16,
          background: "var(--pdf-viewer-bg)",
        }}
      >
        <div style={{ position: "relative", width: "fit-content" }}>
          <canvas
            ref={canvasRef}
            style={{
              background: "#ffffff",
              boxShadow: "var(--shadow-lg)",
              display: "block",
            }}
          />

          {highlights.map((h, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: h.x,
                top: h.y,
                width: h.width,
                height: h.height,
                background: "rgba(255, 215, 0, 0.45)",
                pointerEvents: "none",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

const btn: React.CSSProperties = {
  background: "var(--accent-gradient)",
  border: "none",
  borderRadius: 8,
  padding: "6px 12px",
  color: "var(--panel-text-primary)",
  cursor: "pointer",
  boxShadow: "var(--shadow-lg)",
}