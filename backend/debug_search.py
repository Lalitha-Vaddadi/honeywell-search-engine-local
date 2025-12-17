"""
Simple diagnostic script to debug semantic search issues.
Run directly: python debug_search.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Config from app settings
DB_URL = settings.database_url.replace("+asyncpg", "")
QDRANT_HOST = settings.qdrant_host
QDRANT_PORT = settings.qdrant_port
COLLECTION_NAME = settings.qdrant_collection
EMBEDDING_MODEL = settings.embedding_model_name

def main():
    print("=" * 60)
    print("SEARCH DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Database connection
    print("\n[1] DATABASE CHECK")
    try:
        engine = create_engine(DB_URL, pool_pre_ping=True)
        Session = sessionmaker(bind=engine)
        db = Session()
        print("  ✓ Connected to Postgres")
    except Exception as e:
        print(f"  ✗ Failed to connect to Postgres: {e}")
        return
    
    # 2. Get PDFs
    pdfs = db.execute(text("SELECT id, filename, status FROM pdf_metadata ORDER BY created_at DESC LIMIT 5")).fetchall()
    print(f"\n  Recent PDFs: {len(pdfs)}")
    for pdf in pdfs:
        print(f"    - {pdf.filename} | status={pdf.status} | id={pdf.id}")
    
    if not pdfs:
        print("  ✗ No PDFs found! Upload a document first.")
        return
    
    # Use first PDF
    test_pdf_id = str(pdfs[0].id)
    print(f"\n  Testing with: {pdfs[0].filename}")
    
    # 3. Get chunks
    chunks = db.execute(text("""
        SELECT id, page_num, chunk_index, chunk_type, embedded, 
               LENGTH(chunk_text) as text_len,
               LEFT(chunk_text, 80) as preview
        FROM pdf_chunks 
        WHERE pdf_metadata_id = :pid
        ORDER BY page_num, chunk_index
    """), {"pid": test_pdf_id}).fetchall()
    
    print(f"\n[2] CHUNKS CHECK")
    print(f"  Total chunks: {len(chunks)}")
    
    child_chunks = [c for c in chunks if c.chunk_type == 'CHILD']
    parent_chunks = [c for c in chunks if c.chunk_type == 'PARENT']
    embedded_chunks = [c for c in chunks if c.embedded]
    
    print(f"    - PARENT: {len(parent_chunks)}")
    print(f"    - CHILD: {len(child_chunks)}")
    print(f"    - Embedded: {len(embedded_chunks)}")
    
    if not child_chunks:
        print("  ✗ No CHILD chunks! Check tasks.py chunking logic.")
        return
    
    if not embedded_chunks:
        print("  ✗ No embedded chunks! Check tasks_embedding.py")
        return
    
    # Get a sample chunk text
    sample = db.execute(text("""
        SELECT chunk_text FROM pdf_chunks 
        WHERE pdf_metadata_id = :pid AND chunk_type = 'CHILD' AND embedded = TRUE
        LIMIT 1
    """), {"pid": test_pdf_id}).fetchone()
    
    if sample:
        sample_text = sample.chunk_text
        print(f"\n  Sample chunk text ({len(sample_text)} chars):")
        print(f"    \"{sample_text[:200]}...\"")
    else:
        print("  ✗ Could not get sample chunk text")
        return
    
    # 4. Qdrant check
    print(f"\n[3] QDRANT CHECK")
    try:
        qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        print("  ✓ Connected to Qdrant")
    except Exception as e:
        print(f"  ✗ Failed to connect to Qdrant: {e}")
        return
    
    # Check collection
    try:
        collections = qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        print(f"  Collections: {collection_names}")
        
        if COLLECTION_NAME not in collection_names:
            print(f"  ✗ Collection '{COLLECTION_NAME}' not found!")
            return
        
        collection_info = qdrant.get_collection(COLLECTION_NAME)
        print(f"  Collection '{COLLECTION_NAME}':")
        print(f"    - Points: {collection_info.points_count}")
        print(f"    - Config: {collection_info.config.params}")
    except Exception as e:
        print(f"  ✗ Failed to check collection: {e}")
        import traceback
        traceback.print_exc()
    
    # Get points for this PDF
    try:
        # Use scroll to get points with this pdf_id
        points, _ = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=Filter(must=[FieldCondition(key="pdf_id", match=MatchValue(value=test_pdf_id))]),
            limit=10,
            with_payload=True,
            with_vectors=True,
        )
        print(f"\n  Points for this PDF: {len(points)}")
        
        if not points:
            print("  ✗ No points found in Qdrant for this PDF!")
            print("    Check if embedding task ran successfully.")
            return
        
        # Check vector dimensions
        first_vector = points[0].vector
        print(f"    - Vector dimension: {len(first_vector)}")
        print(f"    - Sample payload: {points[0].payload}")
    except Exception as e:
        print(f"  ✗ Failed to scroll points: {e}")
        return
    
    # 5. Embedding test
    print(f"\n[4] EMBEDDING TEST")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"  ✓ Loaded model: {EMBEDDING_MODEL}")
    except Exception as e:
        print(f"  ✗ Failed to load model: {e}")
        return
    
    # Test with multiple queries
    test_queries = [
        sample_text.split('.')[0].strip()[:100],  # First sentence
        "big data",
        "document processing",
        "question answering system",
        "NVIDIA",
        "embeddings",
    ]
    
    for test_query in test_queries:
        if len(test_query) < 3:
            continue
        print(f"\n  -----")
        print(f"  Query: \"{test_query[:60]}...\"" if len(test_query) > 60 else f"  Query: \"{test_query}\"")
        
        # Embed query
        query_vector = model.encode(test_query).tolist()
        
        # Search with filter
        try:
            q_filter = Filter(should=[FieldCondition(key="pdf_id", match=MatchValue(value=test_pdf_id))])
            results = qdrant.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=3,
                with_payload=True,
                query_filter=q_filter,
            )
            if hasattr(results, 'points'):
                results = results.points
            
            for i, r in enumerate(results):
                score = r.score if hasattr(r, 'score') else 0
                text_preview = (r.payload.get('text', '') or '')[:70]
                print(f"    {i+1}. {score*100:.1f}% | \"{text_preview}...\"")
        except Exception as e:
            print(f"  ✗ Search failed: {e}")
    
    # 6. Search test - REMOVED (integrated into embedding test above)
    
    # 7. Check if query text exists in results
    print(f"\n[6] EXACT MATCH CHECK")
    print(f"  Searching for: \"{test_query[:50]}...\"")
    
    # Get all chunk texts for this PDF
    all_chunks = db.execute(text("""
        SELECT chunk_text FROM pdf_chunks 
        WHERE pdf_metadata_id = :pid AND chunk_type = 'CHILD' AND embedded = TRUE
    """), {"pid": test_pdf_id}).fetchall()
    
    # Check if query text appears in any chunk
    query_lower = test_query.lower()
    matches = []
    for chunk in all_chunks:
        if query_lower in chunk.chunk_text.lower():
            matches.append(chunk.chunk_text[:100])
    
    print(f"  Chunks containing query text: {len(matches)}")
    for m in matches[:3]:
        print(f"    - \"{m}...\"")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
