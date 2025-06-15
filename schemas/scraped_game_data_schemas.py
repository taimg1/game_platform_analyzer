from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enums import GameStatusEnum


class ScrapedGameDataDTO(BaseModel):
    id: UUID
    name_on_platform: str
    price: float
    price_in_usd: float
    currency: str
    availability_status: GameStatusEnum
    url_on_platform: str
    rating: Optional[float]
    reviews_count: Optional[int]
    search_position: Optional[int]
    created_at: datetime
    updated_at: datetime
    special_content_json: Optional[dict]
    discount_info_json: Optional[dict]
    game_id: UUID
    platform_id: UUID

    class Config:
        from_attributes = True


class CreateScrapedGameDataDTO(BaseModel):
    name_on_platform: str
    price: float
    price_in_usd: float
    currency: str
    availability_status: GameStatusEnum
    url_on_platform: str
    rating: Optional[float]
    reviews_count: Optional[int]
    search_position: Optional[int]
    special_content_json: Optional[dict]
    discount_info_json: Optional[dict]
    game_id: UUID
    platform_id: UUID


class ScrapeRequest(BaseModel):
    platform_id: UUID
    limit: int = Field(10, ge=1, le=100, description="Number of games to scrape")
