import uuid
from sqlalchemy import Integer, Text, ForeignKey, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy import text
from app.database import Base


class PDFChunk(Base):
    __tablename__ = "pdf_chunks"

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

    page_num: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    normalized_text: Mapped[str] = mapped_column(Text, nullable=True)

    length_chars: Mapped[int] = mapped_column(Integer, nullable=True)

    token_count: Mapped[int] = mapped_column(Integer, nullable=True)

    chunk_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    parent_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pdf_chunks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    embedded: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    # FULL TEXT SEARCH COLUMN
    lexical_tsv: Mapped[str] = mapped_column(
        TSVECTOR,
        nullable=True,
    )
