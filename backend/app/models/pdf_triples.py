import uuid
from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy import text
from app.database import Base


class PDFTriple(Base):
    __tablename__ = "pdf_triples"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    pdf_metadata_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pdf_metadata.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pdf_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    page_num: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    subject: Mapped[str] = mapped_column(Text, nullable=False)
    predicate: Mapped[str] = mapped_column(Text, nullable=False)
    object: Mapped[str] = mapped_column(Text, nullable=False)

    # FULL TEXT SEARCH FOR TRIPLES
    triple_tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        nullable=True,
    )
