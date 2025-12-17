from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.database_url.replace('+asyncpg',''))
q = text(
    """
    SELECT id, pdf_metadata_id, page_num, chunk_index,
           substring(chunk_text from 1 for 200) AS text,
           ts_rank_cd(lexical_tsv, plainto_tsquery('english', :q)) AS rank
    FROM pdf_chunks
    WHERE chunk_text ILIKE '%' || :pattern || '%'
    ORDER BY rank DESC NULLS LAST
    LIMIT 10;
    """
)
with engine.connect() as conn:
    rows = conn.execute(q, {'q': 'maximize braking torque', 'pattern': 'maximize%braking%torque'}).fetchall()
    for r in rows:
        print(r)
