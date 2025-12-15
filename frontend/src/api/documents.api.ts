import { apiClient } from "@/api";
import type { ApiResponse, Document } from "@/types";

// Add auth header for blob downloads
function authHeaders() {
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const documentsApi = {
  // List PDFs
  getDocuments: () =>
    apiClient.get<ApiResponse<{ documents: Document[]; total: number }>>(
      "/documents"
    ),

  // Get metadata of a PDF
  getDocument: (id: string) =>
    apiClient.get<ApiResponse<Document>>(`/documents/${id}`),

  // Download PDF blob for viewer
  getDocumentFile: (id: string) =>
    apiClient.get<Blob>(`/documents/${id}/file`, {
      responseType: "blob",
      headers: {
        ...authHeaders(),
      },
    }).then(res => res.data), // IMPORTANT: return Blob, not AxiosResponse

  // Upload PDF(s)
  uploadDocuments: (files: File[], onProgress?: (p: number) => void) => {
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));

    return apiClient.post("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        ...authHeaders(),
      },
      onUploadProgress: evt => {
        if (onProgress && evt.total) {
          onProgress(Math.round((evt.loaded * 100) / evt.total));
        }
      },
    });
  },

  // Delete PDF
  deleteDocument: (id: string) =>
    apiClient.delete<ApiResponse>(`/documents/${id}`),
};
