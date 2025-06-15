from uuid import UUID
from sqlalchemy import String, Uuid, JSON, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship

from model.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)

    scraped_data = relationship(
        "ScrapedGameData", back_populates="game", cascade="all, delete-orphan"
    )
