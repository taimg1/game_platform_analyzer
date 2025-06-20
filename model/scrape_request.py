from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Uuid

from model import Base
from enums import ScrapeRequestStatus


class ScrapeRequest(Base):
    __tablename__ = "scrape_requests"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)

    status: Mapped[ScrapeRequestStatus] = mapped_column(
        SQLEnum(
            ScrapeRequestStatus,
            name="scrape_request_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ScrapeRequestStatus.PENDING,
        nullable=False,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
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

    total_games: Mapped[int] = mapped_column(Integer,default=0, nullable=False)
    processed_games: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_scrapes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_scrapes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    platform_id: Mapped[UUID] = mapped_column(
        ForeignKey("platforms.id"), nullable=False
    )

    platform = relationship("Platform", back_populates="scrape_requests")

    game_details = relationship(
        "GameScrapeDetail",
        back_populates="scrape_request",
        cascade="all, delete-orphan",
    )
    result = relationship(
        "ScrapeResult",
        back_populates="scrape_request",
        uselist=False,
        cascade="all, delete-orphan",
    )
