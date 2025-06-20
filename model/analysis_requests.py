from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import Uuid, String, DateTime, JSON
from sqlalchemy.orm import mapped_column, Mapped, relationship

from model.base import Base


class AnalysisRequests(Base):
    __tablename__ = "analysis_requests"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    csv_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    dependent_variable: Mapped[str] = mapped_column(String(100), nullable=False)
    independent_variables: Mapped[str] = mapped_column(JSON, nullable=False)
    formula: Mapped[str] = mapped_column(String(1000), nullable=True)

    results = relationship(
        "RegressionResults", back_populates="request", cascade="all, delete-orphan"
    )
