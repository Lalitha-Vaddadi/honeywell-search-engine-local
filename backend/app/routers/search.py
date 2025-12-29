import time
import uuid
import re
import numpy as np
from typing import List, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentence_transformers.util import cos_sim

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

router = APIRouter(prefix="/search", tags=["Search"])

_SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")

_STOPWORDS = {
    "the", "is", "are", "was", "were", "of", "on", "in", "for", "to",
    "with", "using", "use", "based", "by", "and", "or", "from"
}

def content_tokens(text: str):
    return [
        t for t in _TOKEN_RE.findall(text.lower())
        if t not in _STOPWORDS and len(t) > 2
    ]


def extract_highlight_tokens(sentence: str, query: str):
    """
    Returns stable content tokens to highlight.
    """
    sent_tokens = {
        t for t in _TOKEN_RE.findall(sentence.lower())
        if t not in _STOPWORDS and len(t) > 2
    }

    query_tokens = {
        t for t in _TOKEN_RE.findall(query.lower())
        if t not in _STOPWORDS and len(t) > 2
    }

    # Prefer intersection, fallback to sentence tokens
    tokens = sent_tokens & query_tokens
    if not tokens:
        tokens = sent_tokens

    # Cap to avoid visual noise
    return list(tokens)[:8]

# ----------------------------
# Sentence utils
# ----------------------------
def split_sentences(text: str) -> List[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if len(s.strip()) > 20]


async def best_sentence_score(text: str, query_vec: List[float]):
    sentences = split_sentences(text)
    if not sentences:
        return "", 0.0

    sent_vecs = await embed_query(sentences)
    sims = cos_sim(np.array(query_vec), np.array(sent_vecs))[0]
    idx = int(np.argmax(sims))
    return sentences[idx], float(sims[idx])



# Lexical scoring 
def lexical_sentence_score(sentence: str, query: str) -> float:
    s = sentence.lower()
    q = query.lower()

    # 1. Exact phrase match
    if q in s:
        return 1.0

    s_tokens = content_tokens(s)
    q_tokens = content_tokens(q)

    if not q_tokens:
        return 0.0

    s_set = set(s_tokens)
    q_set = set(q_tokens)

    # 2. All important terms present (dominant lexical signal)
    if q_set.issubset(s_set):
        return 0.9

    # 3. High coverage
    coverage = len(s_set & q_set) / len(q_set)

    if coverage >= 0.75:
        return 0.7
    if coverage >= 0.5:
        return 0.5

    return 0.0


def adjust_semantic_for_lexical(semantic: float, lexical: float) -> float:
    """
    If lexical evidence is strong, semantic should not dominate.
    This prevents 'semantic inflation' on exact matches.
    """
    if lexical >= 0.9:
        return semantic * 0.6
    if lexical >= 0.6:
        return semantic * 0.75
    return semantic

def enforce_lexical_dominance(semantic: float, lexical: float) -> float:
    if lexical >= 0.9 and semantic > lexical:
        return lexical
    return semantic

# ----------------------------
# Confidence composition
# ----------------------------
def final_confidence(semantic: float, lexical: float, oie: float) -> float:
    score = (
        0.55 * semantic +
        0.35 * lexical +
        0.10 * oie
    )
    return max(0.0, min(score, 1.0))


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(default=5, ge=1, le=50)


@router.post("", response_model=ApiResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = time.perf_counter()

    docs = (
        await db.execute(
            select(PDFMetadata).where(
                PDFMetadata.uploaded_by == current_user.id,
                PDFMetadata.status == "COMPLETED",
            )
        )
    ).scalars().all()

    if not docs:
        return ApiResponse(success=True, data={"results": []})

    allowed_ids = [str(doc.id) for doc in docs]
    id_to_doc = {str(doc.id): doc for doc in docs}

    query_vec = await embed_query(request.query)

    semantic_hits = semantic_channel(query_vec, allowed_ids, request.query)
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
        limit=request.limit * 4,
        query=request.query,
    )

    # ----------------------------
    # PAGE-FIRST SELECTION
    # ----------------------------
    pages: Dict[int, list] = {}
    for h in fused:
        pages.setdefault(h["page"], []).append(h)

    page_scores = {}
    for page, hits in pages.items():
        score = 0.0
        for h in hits:
            if h.get("has_lexical"):
                score += 2.0
            if h.get("has_oie"):
                score += 0.5
            if h.get("has_semantic"):
                score += 0.5
        page_scores[page] = score

    ranked_pages = sorted(page_scores, key=page_scores.get, reverse=True)

    candidates = []

    for page in ranked_pages:
        hits = pages[page]

        best = None
        best_sem = 0.0

        for h in hits:
            text = h.get("text") or h.get("parent_text") or ""
            sentence, sem_score = await best_sentence_score(text, query_vec)

            if sem_score > best_sem:
                best_sem = sem_score
                best = (h, sentence, sem_score)

        if not best:
            continue

        h, sentence, sem_score = best

        lex_score = lexical_sentence_score(sentence, request.query)
        oie_score = 1.0 if h.get("has_oie") else 0.0

        adj_sem = adjust_semantic_for_lexical(sem_score, lex_score)
        adj_sem = enforce_lexical_dominance(adj_sem, lex_score)

        confidence = final_confidence(adj_sem, lex_score, oie_score)

        highlight_tokens = extract_highlight_tokens(sentence, request.query)

        candidates.append({
            "documentId": h["pdf_id"],
            "documentName": id_to_doc[h["pdf_id"]].filename,
            "pageNumber": page,
            "snippet": sentence,
            "highlightTokens": highlight_tokens,
            "confidence": confidence,
            "scores": {
                "semantic": round(adj_sem, 3),
                "lexical": round(lex_score, 3),
            },
        })


    # GLOBAL SORT BY CONFIDENCE
    candidates.sort(key=lambda x: x["confidence"], reverse=True)

    results = []
    for c in candidates[:request.limit]:
        results.append({
            "documentId": c["documentId"],
            "documentName": c["documentName"],
            "pageNumber": c["pageNumber"],
            "snippet": c["snippet"],
            "highlightTokens": c["highlightTokens"],
            "confidenceScore": int(c["confidence"] * 100),
            "scores": c["scores"],
        })



    db.add(SearchHistory(user_id=current_user.id, query=request.query))
    await db.commit()

    return ApiResponse(
        success=True,
        data={
            "results": results,
            "totalResults": len(results),
            "searchTime": round(time.perf_counter() - start, 3),
        },
    )
