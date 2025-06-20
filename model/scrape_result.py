from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, ForeignKey, Index, JSON, Uuid

from model import Base


class ScrapeResult(Base):
    __tablename__ = "scrape_results"
    __table_args__ = (
        Index("idx_scrape_result_request", "scrape_request_id", unique=True),
        Index("idx_scrape_result_platform", "platform_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)

    total_games: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_scrapes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_scrapes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    scrape_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    scrape_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("scrape_requests.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    platform_id: Mapped[UUID] = mapped_column(
        ForeignKey("platforms.id"), nullable=False
    )
    scrape_request = relationship("ScrapeRequest", back_populates="result")
    platform = relationship("Platform", back_populates="scrape_results")
