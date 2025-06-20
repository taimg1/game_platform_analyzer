from uuid import UUID

from model import Base
from enums import ScrapeStatus
from sqlalchemy import DateTime, ForeignKey, Enum as SQLEnum, Uuid, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, timezone
from typing import Dict, Any


class GameScrapeDetail(Base):
    __tablename__ = "game_scrape_details"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)

    status: Mapped[ScrapeStatus] = mapped_column(
        SQLEnum(
            ScrapeStatus,
            name="scrape_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=ScrapeStatus.PENDING,
        nullable=False,
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    scrape_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("scrape_requests.id"), nullable=False
    )
    scraped_game_data_id: Mapped[UUID] = mapped_column(
        ForeignKey("scraped_game_data.id"), nullable=True
    )
    scraped_game_data = relationship(
        "ScrapedGameData", back_populates="game_scrape_detail"
    )
    scrape_request = relationship("ScrapeRequest", back_populates="game_details")
