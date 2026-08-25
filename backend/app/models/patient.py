from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from backend.app.database.base import Base


class Patient(Base):

    __tablename__ = "patients"

    id = Column(
        Integer,
        primary_key=True
    )

    first_name = Column(
        String(100),
        nullable=False
    )

    last_name = Column(
        String(100),
        nullable=False
    )

    insurance_number = Column(
        String(50),
        unique=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    cases = relationship(
        "Case",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
