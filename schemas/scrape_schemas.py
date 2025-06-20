from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from enums import ScrapeRequestStatus, ScrapeStatus
from schemas.scraped_game_data_schemas import ScrapedGameDataDTO


class GameScrapeDetailDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID of the game scrape detail")
    scrape_request_id: UUID = Field(..., description="ID of the scrape request")
    scraped_game_data_id: Optional[UUID] = Field(None, description="ID of the scraped game data")
    status: ScrapeStatus = Field(..., description="Scrape status")
    error_message: Optional[str] = Field(None, description="Error message")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")


class ScrapeResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID of the scrape result")
    scrape_request_id: UUID = Field(..., description="ID of the scrape request")
    platform_id: UUID = Field(..., description="ID of the platform")
    total_games: int = Field(..., description="Total number of games")
    successful_scrapes: int = Field(..., description="Number of successful scrapes")
    failed_scrapes: int = Field(..., description="Number of failed scrapes")
    not_found: int = Field(..., description="Number of games not found")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    scrape_metadata: Optional[Dict[str, Any]] = Field(None, description="Scrape metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    scraped_games: List[ScrapedGameDataDTO] = Field([], description="List of scraped games")



class ScrapeRequestDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="ID of the scrape request")
    platform_id: UUID = Field(..., description="ID of the platform")
    status: ScrapeRequestStatus = Field(..., description="Scrape request status")
    total_games: Optional[int] = Field(0, description="Total number of games")
    processed_games: Optional[int] = Field(0, description="Number of processed games")
    successful_scrapes: Optional[int] = Field(0, description="Number of successful scrapes")
    failed_scrapes: Optional[int] = Field(0, description="Number of failed scrapes")
    error_message: Optional[str] = Field(None, description="Error message")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    results: List[ScrapedGameDataDTO] = Field([], description="List of scrape results")
    scrape_details: List[GameScrapeDetailDTO] = Field([], description="List of scrape details")
