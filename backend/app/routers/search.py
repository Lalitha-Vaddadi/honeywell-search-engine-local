import time
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import fitz  # PyMuPDF
import tempfile
import os

from app.database import get_db
from app.dependencies import get_current_user
from app.models import PDFMetadata
from app.models.search_history import SearchHistory
from app.models.user import User
from app.schemas import ApiResponse
from app.services.embeddings.embedder import embed_query
from app.services.search.fusion import (
    semantic_channel,
    lexical_channel,
    triple_channel,
    fuse_results,
)
from app.config import settings
from minio import Minio

router = APIRouter(prefix="/search", tags=["Search"])

# ------------------------------------------------------------------
# MinIO client (read-only)
# ------------------------------------------------------------------
minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=False,
)

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def normalize(text: str) -> str:
    return " ".join(
        text.lower()
        .translate(str.maketrans("", "", r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""))
        .split()
    )


def extract_highlight_boxes(
    object_key: str,
    page_number: int,
    query_text: str,
) -> list[dict]:
    """
    Returns normalized bounding boxes for the first text match on the page.
    Coordinates are normalized (0–1), top-left origin.
    """
    if not query_text:
        return []

    tmp_path = None
    boxes = []

    try:
        # Download PDF to temp
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp_path = tmp.name
        tmp.close()

        resp = minio_client.get_object(settings.minio_bucket, object_key)
        with open(tmp_path, "wb") as f:
            for chunk in resp.stream(32 * 1024):
                f.write(chunk)
        resp.close()
        resp.release_conn()

        doc = fitz.open(tmp_path)
        page_index = max(0, page_number - 1)
        if page_index >= len(doc):
            return []

        page = doc[page_index]
        page_width = page.rect.width
        page_height = page.rect.height

        target = normalize(query_text)

        # Word-level search (robust)
        words = page.get_text("words")  # (x0,y0,x1,y1,word,...)
        normalized_words = [(w, normalize(w[4])) for w in words]

        window = []
        window_text = ""

        for w, norm in normalized_words:
            if not norm:
                continue
            window.append(w)
            window_text += norm + " "

            if len(window_text) > len(target) + 20:
                window.pop(0)
                window_text = " ".join(normalize(x[4]) for x in window) + " "

            if target in window_text:
                # Compute union bbox
                x0 = min(w[0] for w in window)
                y0 = min(w[1] for w in window)
                x1 = max(w[2] for w in window)
                y1 = max(w[3] for w in window)

                boxes.append({
                    "x": x0 / page_width,
                    "y": y0 / page_height,
                    "w": (x1 - x0) / page_width,
                    "h": (y1 - y0) / page_height,
                })
                break

        doc.close()
        return boxes

    except Exception:
        return []

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# ------------------------------------------------------------------
# API
# ------------------------------------------------------------------
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    documentIds: Optional[List[str]] = None
    limit: int = Field(default=5, ge=1, le=50)


@router.post("", response_model=ApiResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = time.perf_counter()

    doc_query = select(PDFMetadata).where(
        PDFMetadata.uploaded_by == current_user.id,
        PDFMetadata.status == "COMPLETED",
    )

    result = await db.execute(doc_query)
    docs = result.scalars().all()

    if not docs:
        return ApiResponse(success=True, data={"results": []}, message=None)

    allowed_ids = [str(doc.id) for doc in docs]
    id_to_doc = {str(doc.id): doc for doc in docs}

    query_vector = await embed_query(request.query)

    semantic_hits = semantic_channel(query_vector, allowed_ids)
    lexical_hits = await lexical_channel(
        db, request.query, [uuid.UUID(pid) for pid in allowed_ids]
    )
    triple_hits = await triple_channel(
        db, request.query, [uuid.UUID(pid) for pid in allowed_ids]
    )

    fused = fuse_results(
        semantic_hits,
        lexical_hits,
        triple_hits,
        request.limit,
        query=request.query,
    )

    results = []

    for h in fused:
        pdf_id = h.get("pdf_id")
        if not pdf_id or pdf_id not in id_to_doc:
            continue

        page_num = h.get("page") or 1
        raw_text = h.get("chunk_text") or h.get("snippet") or ""

        pdf_meta = id_to_doc[pdf_id]

        highlight_boxes = extract_highlight_boxes(
            object_key=pdf_meta.object_key,
            page_number=page_num,
            query_text=raw_text,
        )

        results.append({
            "documentId": pdf_id,
            "documentName": pdf_meta.filename,
            "pageNumber": page_num,
            "snippet": raw_text[:300],
            "highlightBoxes": highlight_boxes,
            "confidenceScore": max(
                0.0,
                min(100.0, (h.get("fusion_score") or 0) * 100),
            ),
            "scores": {
                "semantic": h.get("semantic_score", 0),
                "lexical": h.get("lexical_score", 0),
                "triple": h.get("triple_score", 0),
            },
        })

    db.add(SearchHistory(user_id=current_user.id, query=request.query))
    await db.commit()

    return ApiResponse(
        success=True,
        data={
            "results": results,
            "totalResults": len(results),
            "searchTime": time.perf_counter() - start,
        },
        message=None,
    )
