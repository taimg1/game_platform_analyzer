from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Uuid
from model import Base


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    base_url: Mapped[str] = mapped_column(String(150), nullable=False)
    search_url_template: Mapped[str] = mapped_column(String(150), nullable=False)
    game_data_selector: Mapped[str] = mapped_column(String(150), nullable=False)

    scraped_data = relationship(
        "ScrapedGameData", back_populates="platform", cascade="all, delete-orphan"
    )
