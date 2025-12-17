"""
Diagnostic test for semantic search pipeline.
Tests the entire flow: DB chunks -> embeddings -> Qdrant -> search results
"""
import sys
import pathlib

# Ensure backend package is importable
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import create_engine, text as sql_text
from sqlalchemy.orm import sessionmaker
from qdrant_client import QdrantClient

from app.config import settings
from app.services.embeddings.embedder import generate_embeddings

# ============================================================
# Setup
# ============================================================
SYNC_DB_URL = settings.database_url.replace("+asyncpg", "")
engine = create_engine(SYNC_DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
COLLECTION_NAME = settings.qdrant_collection


def diagnose_search():
    db = SessionLocal()
    
    print("=" * 60)
    print("SEMANTIC SEARCH DIAGNOSTIC")
    print("=" * 60)
    
    # --------------------------------------------------------
    # Step 1: Check what's in the database
    # --------------------------------------------------------
    print("\n[1] DATABASE STATUS")
    
    # Get PDF metadata
    pdfs = db.execute(sql_text("""
        SELECT id, filename, status, error_message 
        FROM pdf_metadata 
        ORDER BY created_at DESC 
        LIMIT 5
    """)).fetchall()
    
    print(f"  PDFs in database: {len(pdfs)}")
    for pdf in pdfs:
        print(f"    - {pdf.filename[:50]}: status={pdf.status}, id={pdf.id}")
    
    if not pdfs:
        print("  ERROR: No PDFs found!")
        return
    
    pdf_id = str(pdfs[0].id)
    print(f"\n  Using most recent PDF: {pdf_id}")
    
    # Get chunks for this PDF
    chunks = db.execute(sql_text("""
        SELECT id, page_num, chunk_index, chunk_type, embedded, 
               LEFT(chunk_text, 100) as text_preview,
               LENGTH(chunk_text) as text_len
        FROM pdf_chunks 
        WHERE pdf_metadata_id = :pid
        ORDER BY page_num, chunk_index
    """), {"pid": pdf_id}).fetchall()
    
    print(f"\n  Chunks for this PDF: {len(chunks)}")
    child_chunks = [c for c in chunks if c.chunk_type == 'CHILD']
    parent_chunks = [c for c in chunks if c.chunk_type == 'PARENT']
    embedded_chunks = [c for c in chunks if c.embedded]
    
    print(f"    - PARENT chunks: {len(parent_chunks)}")
    print(f"    - CHILD chunks: {len(child_chunks)}")
    print(f"    - Embedded: {len(embedded_chunks)}")
    
    if not child_chunks:
        print("  ERROR: No CHILD chunks found! Embedding only processes CHILD chunks.")
        return
    
    if not embedded_chunks:
        print("  ERROR: No chunks marked as embedded!")
        return
    
    # Sample chunk text
    sample_chunk = db.execute(sql_text("""
        SELECT chunk_text FROM pdf_chunks 
        WHERE pdf_metadata_id = :pid AND chunk_type = 'CHILD'
        LIMIT 1
    """), {"pid": pdf_id}).fetchone()
    
    if sample_chunk:
        print(f"\n  Sample chunk text (first 200 chars):")
        print(f"    '{sample_chunk.chunk_text[:200]}...'")
    
    # --------------------------------------------------------
    # Step 2: Check Qdrant collection
    # --------------------------------------------------------
    print("\n[2] QDRANT STATUS")
    
    try:
        collections = qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        print(f"  Collections: {collection_names}")
        
        if COLLECTION_NAME not in collection_names:
            print(f"  ERROR: Collection '{COLLECTION_NAME}' not found!")
            return
        
        collection_info = qdrant.get_collection(COLLECTION_NAME)
        print(f"  Collection '{COLLECTION_NAME}':")
        print(f"    - Vector size: {collection_info.config.params.vectors.size}")
        print(f"    - Distance: {collection_info.config.params.vectors.distance}")
        print(f"    - Points count: {collection_info.points_count}")
        
        if collection_info.points_count == 0:
            print("  ERROR: Collection has 0 points! Embeddings not stored.")
            return
            
    except Exception as e:
        print(f"  ERROR connecting to Qdrant: {e}")
        return
    
    # --------------------------------------------------------
    # Step 3: Check if PDF's chunks are in Qdrant
    # --------------------------------------------------------
    print("\n[3] QDRANT POINTS FOR THIS PDF")
    
    try:
        # Scroll to find points with this pdf_id
        scroll_result = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
                "must": [{"key": "pdf_id", "match": {"value": pdf_id}}]
            },
            limit=10,
            with_payload=True,
            with_vectors=False,
        )
        
        points = scroll_result[0]
        print(f"  Points for pdf_id={pdf_id}: {len(points)}")
        
        if points:
            for i, p in enumerate(points[:3]):
                text_preview = p.payload.get("text", "")[:80] if p.payload else ""
                print(f"    Point {i+1}: page={p.payload.get('page')}, text='{text_preview}...'")
        else:
            print("  ERROR: No points found for this PDF in Qdrant!")
            print("  The embedding task may not have run, or failed silently.")
            return
            
    except Exception as e:
        print(f"  ERROR scrolling Qdrant: {e}")
        return
    
    # --------------------------------------------------------
    # Step 4: Test embedding generation
    # --------------------------------------------------------
    print("\n[4] EMBEDDING GENERATION TEST")
    
    test_query = "big data"
    print(f"  Test query: '{test_query}'")
    
    try:
        query_embedding = generate_embeddings([test_query])[0]
        print(f"  Query embedding dimension: {len(query_embedding)}")
        print(f"  First 5 values: {query_embedding[:5]}")
        
        if len(query_embedding) != collection_info.config.params.vectors.size:
            print(f"  ERROR: Embedding dim {len(query_embedding)} != collection dim {collection_info.config.params.vectors.size}")
            return
            
    except Exception as e:
        print(f"  ERROR generating embedding: {e}")
        return
    
    # --------------------------------------------------------
    # Step 5: Test search (unfiltered)
    # --------------------------------------------------------
    print("\n[5] SEARCH TEST (UNFILTERED)")
    
    try:
        results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=5,
            with_payload=True,
        )
        
        if hasattr(results, "points"):
            results = results.points
        
        print(f"  Results returned: {len(results)}")
        
        for i, r in enumerate(results):
            score = r.score if hasattr(r, "score") else "N/A"
            text = r.payload.get("text", "")[:100] if r.payload else ""
            pdf = r.payload.get("pdf_id", "")[:8] if r.payload else ""
            print(f"    {i+1}. score={score:.4f}, pdf={pdf}..., text='{text}...'")
            
    except Exception as e:
        print(f"  ERROR searching: {e}")
        return
    
    # --------------------------------------------------------
    # Step 6: Test search (filtered to this PDF)
    # --------------------------------------------------------
    print("\n[6] SEARCH TEST (FILTERED TO THIS PDF)")
    
    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=5,
            with_payload=True,
            query_filter=Filter(
                should=[FieldCondition(key="pdf_id", match=MatchValue(value=pdf_id))]
            ),
        )
        
        if hasattr(results, "points"):
            results = results.points
        
        print(f"  Results returned: {len(results)}")
        
        for i, r in enumerate(results):
            score = r.score if hasattr(r, "score") else "N/A"
            text = r.payload.get("text", "")[:100] if r.payload else ""
            page = r.payload.get("page", "?") if r.payload else "?"
            print(f"    {i+1}. score={score:.4f}, page={page}, text='{text}...'")
            
    except Exception as e:
        print(f"  ERROR searching with filter: {e}")
        return
    
    # --------------------------------------------------------
    # Step 7: Search for exact text from chunk
    # --------------------------------------------------------
    print("\n[7] EXACT TEXT SEARCH TEST")
    
    if sample_chunk:
        # Take first sentence from sample chunk
        sample_text = sample_chunk.chunk_text.split('.')[0][:100]
        print(f"  Searching for exact chunk text: '{sample_text}'")
        
        try:
            exact_embedding = generate_embeddings([sample_text])[0]
            
            results = qdrant.query_points(
                collection_name=COLLECTION_NAME,
                query=exact_embedding,
                limit=5,
                with_payload=True,
            )
            
            if hasattr(results, "points"):
                results = results.points
            
            print(f"  Results returned: {len(results)}")
            
            for i, r in enumerate(results):
                score = r.score if hasattr(r, "score") else "N/A"
                text = r.payload.get("text", "")[:80] if r.payload else ""
                print(f"    {i+1}. score={score:.4f}, text='{text}...'")
                
            if results and results[0].score < 0.7:
                print("\n  WARNING: Low similarity even for exact text!")
                print("  This suggests embeddings may not be stored correctly.")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # --------------------------------------------------------
    # Step 8: Compare stored embedding with fresh embedding
    # --------------------------------------------------------
    print("\n[8] EMBEDDING CONSISTENCY CHECK")
    
    if points:
        # Get a point with its vector
        point_with_vector = qdrant.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[points[0].id],
            with_vectors=True,
            with_payload=True,
        )
        
        if point_with_vector:
            stored_text = point_with_vector[0].payload.get("text", "")
            stored_vector = point_with_vector[0].vector
            
            print(f"  Stored text: '{stored_text[:80]}...'")
            print(f"  Stored vector dim: {len(stored_vector)}")
            
            # Re-embed the same text
            fresh_vector = generate_embeddings([stored_text])[0]
            
            # Calculate cosine similarity
            import math
            dot = sum(a * b for a, b in zip(stored_vector, fresh_vector))
            norm1 = math.sqrt(sum(a * a for a in stored_vector))
            norm2 = math.sqrt(sum(a * a for a in fresh_vector))
            similarity = dot / (norm1 * norm2) if norm1 and norm2 else 0
            
            print(f"  Fresh vector dim: {len(fresh_vector)}")
            print(f"  Similarity (stored vs fresh): {similarity:.4f}")
            
            if similarity < 0.99:
                print("  WARNING: Embeddings differ! Model may have changed.")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    
    db.close()


if __name__ == "__main__":
    diagnose_search()
