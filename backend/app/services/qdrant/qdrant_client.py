from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http import models
from app.config import settings

COLLECTION_NAME = settings.qdrant_collection
VECTOR_SIZE = settings.embedding_dim  # must align with embedding model

client = QdrantClient(
    host=settings.qdrant_host,
    port=settings.qdrant_port,
)

def ensure_collection():
    collections = client.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
        print(f"[QDRANT] Created collection '{COLLECTION_NAME}' with dim={VECTOR_SIZE}")
    else:
        print(f"[QDRANT] Collection '{COLLECTION_NAME}' already exists")

def upsert_points(points: list[dict]):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
        wait=True,
    )


def delete_pdf_vectors(pdf_id: str):
    """Delete all vectors in Qdrant for a given pdf_id payload."""
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[models.FieldCondition(key="pdf_id", match=models.MatchValue(value=pdf_id))]
            )
        ),
        wait=True,
    )
