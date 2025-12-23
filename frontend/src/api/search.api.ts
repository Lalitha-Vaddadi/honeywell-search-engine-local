import api from "./client"
import type { SearchResult } from "@/types"

interface SearchResponse {
  results: SearchResult[]
  totalResults: number
  searchTime: number
}

export async function searchDocuments(
  query: string,
  limit = 10
): Promise<SearchResponse> {
  const response = await api.post("/search", {
    query,
    limit,
  })

  const data = response.data?.data

  if (!data) {
    return {
      results: [],
      totalResults: 0,
      searchTime: 0,
    }
  }

  const results: SearchResult[] = data.results.map((r: any) => ({
    documentId: r.documentId,
    documentName: r.documentName,
    pageNumber: r.pageNumber,
    snippet: r.snippet,
    highlightText: r.highlightText || "",
    rawChunkText: r.rawChunkText || "",
    confidenceScore: r.confidenceScore,
    scores: r.scores,
  }))

  return {
    results,
    totalResults: data.totalResults,
    searchTime: data.searchTime,
  }
}
