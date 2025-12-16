from qdrant_client import QdrantClient

qdrant = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "pdf_chunks"


def semantic_search(query_vector: list[float], top_k: int = 5):
    results = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True,
    )

    formatted = []
    for r in results:
        formatted.append({
            "score": r.score,
            "pdf_id": r.payload.get("pdf_id"),
            "page": r.payload.get("page"),
            "chunk_index": r.payload.get("chunk_index"),
            "text": r.payload.get("text"),
        })

    return formatted
