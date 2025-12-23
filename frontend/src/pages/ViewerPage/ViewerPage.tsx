import { useEffect, useMemo, useRef, useState } from "react"
import { useParams, useNavigate, useLocation } from "react-router-dom"
import { Document, Page, pdfjs } from "react-pdf"
import {
  HiArrowLeft,
  HiChevronLeft,
  HiChevronRight,
  HiZoomIn,
  HiZoomOut,
} from "react-icons/hi"
import { documentsApi } from "@/api"
import { ROUTES } from "@/utils/constants"
import styles from "./ViewerPage.module.css"

import "react-pdf/dist/Page/TextLayer.css"
import "react-pdf/dist/Page/AnnotationLayer.css"

/* --------------------------------------------------
   PDF worker
-------------------------------------------------- */
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.js",
  import.meta.url
).toString()

/* --------------------------------------------------
   Normalization (must match backend)
-------------------------------------------------- */
const normalize = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^\w\s]/g, "")
    .replace(/\s+/g, " ")
    .trim()

interface ViewerPageProps {
  documentIdOverride?: string
  pageOverride?: number
  highlightTextOverride?: string | null
  embedded?: boolean
}

export default function ViewerPage({
  documentIdOverride,
  pageOverride,
  highlightTextOverride,
  embedded = false,
}: ViewerPageProps) {
  const params = useParams<{ documentId: string }>()
  const location = useLocation()
  const navigate = useNavigate()

  const documentId = documentIdOverride || params.documentId

  const highlightRaw =
    highlightTextOverride ??
    (location.state as any)?.highlightText ??
    ""

  const highlightText = useMemo(
    () => normalize(highlightRaw),
    [highlightRaw]
  )

  const pageContainerRef = useRef<HTMLDivElement>(null)

  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null)
  const [numPages, setNumPages] = useState(0)
  const [page, setPage] = useState(pageOverride || 1)
  const [scale, setScale] = useState(1.0)
  const [docName, setDocName] = useState("")
  const [error, setError] = useState<string | null>(null)

  /* -------- Load PDF -------- */
  useEffect(() => {
    if (!documentId) return

    const load = async () => {
      try {
        const meta = await documentsApi.getDocument(documentId)
        setDocName(meta.data.filename)

        const blob = await documentsApi.getDocumentFile(documentId)
        setPdfBlob(blob)

        if (pageOverride) {
          setPage(pageOverride)
        }
      } catch {
        setError("Failed to load PDF")
      }
    }

    load()
  }, [documentId, pageOverride])

  /* -------- Highlight text (text layer) -------- */
  useEffect(() => {
    if (!highlightText || !pageContainerRef.current) return

    const timeout = setTimeout(() => {
      const container = pageContainerRef.current!

      const spans = Array.from(
        container.querySelectorAll<HTMLSpanElement>(
          ".react-pdf__Page__textContent span"
        )
      )

      spans.forEach(s => (s.innerHTML = s.textContent || ""))

      const fullText = spans
        .map(s => normalize(s.textContent || ""))
        .join(" ")

      const matchIndex = fullText.indexOf(highlightText)
      if (matchIndex === -1) return

      let charPos = 0
      let firstHit: HTMLElement | null = null

      for (const span of spans) {
        const raw = span.textContent || ""
        const norm = normalize(raw)

        const start = charPos
        const end = charPos + norm.length

        if (
          end >= matchIndex &&
          start <= matchIndex + highlightText.length &&
          raw.trim()
        ) {
          span.innerHTML = `<mark style="background:#ffe58a;padding:0;">${raw}</mark>`
          if (!firstHit) firstHit = span
        }

        charPos += norm.length + 1
      }

      firstHit?.scrollIntoView({ behavior: "smooth", block: "center" })
    }, 300)

    return () => clearTimeout(timeout)
  }, [highlightText, page, scale])

  if (error) {
    return <div className={styles.error}>{error}</div>
  }

  return (
    <div className={styles.container}>
      {/* -------- Toolbar -------- */}
      {!embedded && (
        <div className={styles.toolbar}>
          <button
            className={styles.iconBtn}
            onClick={() => navigate(ROUTES.DASHBOARD)}
          >
            <HiArrowLeft size={18} />
          </button>

          <span className={styles.title}>{docName}</span>

          <div className={styles.controls}>
            <button
              className={styles.iconBtn}
              disabled={page <= 1}
              onClick={() => setPage(p => p - 1)}
            >
              <HiChevronLeft size={20} />
            </button>

            <span>
              {page} / {numPages}
            </span>

            <button
              className={styles.iconBtn}
              disabled={page >= numPages}
              onClick={() => setPage(p => p + 1)}
            >
              <HiChevronRight size={20} />
            </button>

            <button
              className={styles.iconBtn}
              onClick={() => setScale(s => Math.max(0.5, s - 0.25))}
            >
              <HiZoomOut size={18} />
            </button>

            <span>{Math.round(scale * 100)}%</span>

            <button
              className={styles.iconBtn}
              onClick={() => setScale(s => Math.min(3, s + 0.25))}
            >
              <HiZoomIn size={18} />
            </button>
          </div>
        </div>
      )}

      {/* -------- Viewer -------- */}
      <div className={styles.viewer}>
        {pdfBlob && (
          <Document
            file={pdfBlob}
            onLoadSuccess={({ numPages }) => setNumPages(numPages)}
          >
            <div ref={pageContainerRef}>
              <Page
                pageNumber={page}
                scale={scale}
                renderAnnotationLayer={false}
              />
            </div>
          </Document>
        )}
      </div>
    </div>
  )
}
