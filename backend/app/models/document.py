from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text

from backend.app.database.base import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True
    )

    case_id = Column(
        Integer,
        ForeignKey("cases.id"),
        nullable=False
    )

    filename = Column(
        String(255),
        nullable=False
    )

    document_type = Column(
        String(100)
    )

    content = Column(
        Text
    )

    embedding_id = Column(
        String(255)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
