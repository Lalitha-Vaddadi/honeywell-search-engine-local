import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { HiUpload, HiTrash } from "react-icons/hi";
import { documentsApi } from "@/api";
import { formatFileSize } from "@/utils/formatters";
import { FILE_LIMITS } from "@/utils/constants";
import type { Document } from "@/types";
import { Loader } from "@/components/common";

export function LeftPanelDocuments({
  onSelectDocument,
}: {
  onSelectDocument?: (id: string) => void;
}) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      const res = await documentsApi.getDocuments();
      setDocuments(res.data?.documents ?? []);
    } catch (e) {
      console.error("Failed to load documents", e);
      setDocuments([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  // Poll only while documents are processing
  useEffect(() => {
    const hasActiveDocs = documents.some(
      d => d.status === "pending" || d.status === "processing"
    );

    if (!hasActiveDocs) return;

    const interval = setInterval(() => {
      fetchDocuments();
    }, 3000);

    return () => clearInterval(interval);
  }, [documents, fetchDocuments]);

  const onDrop = useCallback(
    async (files: File[]) => {
      if (!files.length) return;
      setIsUploading(true);
      setUploadProgress(0);
      try {
        await documentsApi.uploadDocuments(files, p => setUploadProgress(p));
        await fetchDocuments();
      } finally {
        setIsUploading(false);
        setUploadProgress(null);
      }
    },
    [fetchDocuments]
  );

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: FILE_LIMITS.ACCEPTED_TYPES,
    maxSize: FILE_LIMITS.MAX_FILE_SIZE,
    disabled: isUploading,
  });

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this PDF?")) return;
    await documentsApi.deleteDocument(id);
    setDocuments(prev => prev.filter(d => d.id !== id));
  };

  return (
    <div style={{ padding: 16, color: "var(--panel-text-primary)" }}>
      <div
        {...getRootProps()}
        style={{
          borderRadius: 14,
          padding: 14,
          marginBottom: 16,
          cursor: "pointer",
          background: "var(--accent-gradient)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: "50%",
              background: "rgba(255,255,255,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <HiUpload size={18} />
          </div>

          <div>
            <div style={{ fontWeight: 600 }}>Upload PDFs</div>
            <div style={{ fontSize: 12, color: "var(--panel-text-muted)" }}>
              Drag & drop or click to browse
            </div>
          </div>
        </div>

        <input {...getInputProps()} />
      </div>

      {isUploading && uploadProgress !== null && (
        <div style={{ marginBottom: 14 }}>
          <div
            style={{
              height: 6,
              borderRadius: 6,
              background: "var(--panel-border)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${uploadProgress}%`,
                background: "#22c55e",
                transition: "width 0.2s",
              }}
            />
          </div>
        </div>
      )}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <h3 style={{ margin: 0, fontSize: 15 }}>Your PDFs</h3>
        <button
          onClick={async () => {
            if (!confirm("Delete all PDFs?")) return;
            await documentsApi.deleteAllDocuments();
            setDocuments([]);
          }}
          style={{
            background: "none",
            border: "none",
            color: "var(--danger)",
            cursor: "pointer",
            fontSize: 13,
            fontWeight: 600,
          }}
        >
          Clear All
        </button>
      </div>

      {isLoading ? (
        <Loader text="Loading..." />
      ) : documents.length === 0 ? (
        <p style={{ color: "var(--panel-text-muted)" }}>
          No documents uploaded
        </p>
      ) : (
        documents.map(doc => (
          <div
            key={doc.id}
            style={{
              background: "var(--accent-gradient)",
              borderRadius: 14,
              padding: 10,
              marginBottom: 8,
              display: "flex",
              gap: 10,
              boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
            }}
          >
            <div
              onClick={() => onSelectDocument?.(doc.id)}
              style={{
                cursor: "pointer",
                flex: 1,
                minWidth: 0,
              }}
            >
              <div
                style={{
                  fontWeight: 600,
                  fontSize: 13,
                  marginBottom: 4,
                  whiteSpace: "normal",
                  wordBreak: "break-word",
                }}
              >
                {doc.filename}
              </div>

              <div style={{ fontSize: 12, color: "var(--panel-text-muted)" }}>
                {formatFileSize(doc.file_size)} •{" "}
                {new Date(doc.created_at + "Z").toLocaleString("en-IN", {
                  dateStyle: "medium",
                  timeStyle: "medium",
                })}
              </div>

              {doc.status === "pending" && (
                <div style={{ fontSize: 11, color: "#f59e0b", marginTop: 4 }}>
                  Uploading…
                </div>
              )}

              {doc.status === "processing" && (
                <div style={{ fontSize: 11, color: "#3b82f6", marginTop: 4 }}>
                  Extracting text…
                </div>
              )}

              {doc.status === "completed" && (
                <div style={{ fontSize: 11, color: "#22c55e", marginTop: 4 }}>
                  Ready
                </div>
              )}
            </div>

            <button
              onClick={() => handleDelete(doc.id)}
              style={{
                background: "none",
                border: "none",
                color: "var(--danger)",
                cursor: "pointer",
              }}
            >
              <HiTrash size={18} />
            </button>
          </div>
        ))
      )}
    </div>
  );
}

export default LeftPanelDocuments;
