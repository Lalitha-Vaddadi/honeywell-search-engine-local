import React, { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { HiUpload, HiDocumentText, HiTrash } from 'react-icons/hi';
import { documentsApi } from '@/api';
import { formatFileSize, formatRelativeTime } from '@/utils/formatters';
import { FILE_LIMITS } from '@/utils/constants';
import type { Document } from '@/types';
import { Button, Loader } from '@/components/common';
import styles from '@/pages/DocumentsPage/DocumentsPage.module.css';



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
      const response = await documentsApi.getDocuments();
      setDocuments(response.data.data.documents);
    } catch {}
    finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;
      setIsUploading(true);
      setUploadProgress(0);
      try {
        await documentsApi.uploadDocuments(acceptedFiles, (p) => setUploadProgress(p));
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
    if (!confirm('Delete this PDF?')) return;
    await documentsApi.deleteDocument(id);
    setDocuments(prev => prev.filter(d => d.id !== id));
  };

  return (
    <div style={{ padding: '16px', width: '100%' }}>

      {/* NEW UPLOAD BAR */}
      <div
        {...getRootProps()}
        style={{
          padding: '12px 16px',
          border: '1px solid var(--color-border)',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          marginBottom: '20px',
          background: 'white',
        }}
      >
        <span style={{ fontWeight: 600 }}>Upload PDFs</span>
        <HiUpload size={20} />
        <input {...getInputProps()} />
      </div>

      {isUploading && uploadProgress !== null && (
        <div style={{ marginBottom: '12px' }}>
          <div style={{ height: '5px', background: '#ddd' }}>
            <div style={{
              height: '100%',
              width: `${uploadProgress}%`,
              background: 'var(--color-primary)',
              transition: 'width 0.2s'
            }} />
          </div>
          <p style={{ fontSize: 12 }}>{uploadProgress}%</p>
        </div>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "10px",
        }}
      >
        <h3 style={{ margin: 0 }}>Your PDFs</h3>

        <button
          onClick={async () => {
            if (!confirm("Delete all PDFs? This cannot be undone.")) return;
            await documentsApi.deleteAllDocuments();
            setDocuments([]);
          }}
          style={{
            color: "var(--color-error)",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Clear All
        </button>
      </div>


      {isLoading ? <Loader text="Loading..." /> : documents.length === 0 ? (
        <p>No documents</p>
      ) : (
        documents.map(doc => (
          <div
            key={doc.id}
            style={{
              padding: '10px 0',
              borderBottom: '1px solid var(--color-border)',
              display: 'flex',
              justifyContent: 'space-between',
              gap: '8px'
            }}
          >
            <div
              onClick={() => onSelectDocument?.(doc.id)}
              style={{ cursor: 'pointer', flex: 1 }}
            >
              {/* show FULL filename */}
              <div style={{
                fontWeight: 600,
                whiteSpace: 'normal',
                wordBreak: 'break-word'
              }}>
                {doc.filename}
              </div>

                <div style={{ fontSize: 12, color: 'var(--color-text-secondary)' }}>
                    {formatFileSize(doc.file_size)} • {formatRelativeTime(doc.created_at)}
              </div>

            </div>

            <button
              onClick={() => handleDelete(doc.id)}
              style={{ background: 'none', border: 'none', color: 'var(--color-error)' }}
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
