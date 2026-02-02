import api from "./client"

export const documentsApi = {
  async getDocuments() {
    const res = await api.get("/documents")

    // Normalize backend enum casing to match frontend DocumentStatus
    if (res.data?.data?.documents) {
      res.data.data.documents = res.data.data.documents.map((doc: any) => ({
        ...doc,
        status: String(doc.status).toLowerCase(),
      }))
    }

    return res.data
  },

  async getDocument(documentId: string) {
    const res = await api.get(`/documents/${documentId}`)

    // Normalize single document status
    if (res.data?.data?.status) {
      res.data.data.status = String(res.data.data.status).toLowerCase()
    }

    return res.data
  },

  async getDocumentFile(documentId: string): Promise<Blob> {
    const res = await api.get(`/documents/${documentId}/file`, {
      responseType: "arraybuffer",
    })

    const buffer = res.data
    if (!buffer) throw new Error("Empty PDF response")

    try {
      const blob = new Blob([buffer], { type: "application/pdf" })
      return blob
    } catch {
      const res = await api.get(`/documents/${documentId}/file`, {
        responseType: "blob",
      })
      if (!(res.data instanceof Blob)) {
        throw new Error("PDF response is not a Blob")
      }
      return res.data
    }
  },

  async deleteAllDocuments() {
    const res = await api.delete(`/documents`)
    return res.data
  },

  async uploadDocuments(
    files: File[],
    onProgress?: (percent: number) => void
  ) {
    const formData = new FormData()
    files.forEach((file) => formData.append("files", file))

    const res = await api.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (!onProgress || !e.total) return
        onProgress(Math.round((e.loaded * 100) / e.total))
      },
    })

    return res.data
  },

  async deleteDocument(documentId: string) {
    const res = await api.delete(`/documents/${documentId}`)
    return res.data
  },
}
