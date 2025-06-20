from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Uuid, JSON, ForeignKey, Index, Enum, DateTime
from typing import Optional
from datetime import datetime, timezone
from model import Base
from enums import GameStatusEnum


class ScrapedGameData(Base):
    __tablename__ = "scraped_game_data"
    __table_args__ = (Index("ix_unique_game_platform", "game_id", "platform_id"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)

    name_on_platform: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    price_in_usd: Mapped[float] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=True)
    availability_status: Mapped[GameStatusEnum] = mapped_column(
        Enum(
            GameStatusEnum,
            name="availability_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    url_on_platform: Mapped[str] = mapped_column(String(255), nullable=False)

    rating: Mapped[Optional[float]] = mapped_column(nullable=True)
    reviews_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    search_position: Mapped[Optional[int]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    special_content_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    discount_info_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    game_id: Mapped[UUID] = mapped_column(ForeignKey("games.id"))
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))

    game = relationship("Game", back_populates="scraped_data")
    platform = relationship("Platform", back_populates="scraped_data")
    game_scrape_detail = relationship("GameScrapeDetail", back_populates="scraped_game_data")
