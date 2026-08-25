from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.database.base import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id"),
        nullable=False
    )

    case_type = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        default="OPEN"
    )

    priority = Column(
        String(20),
        default="NORMAL"
    )

    description = Column(
        Text,
        nullable=True
    )


    patient = relationship(
        "Patient",
        back_populates="cases"
    )
