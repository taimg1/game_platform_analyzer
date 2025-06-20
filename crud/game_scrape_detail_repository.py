from typing import Annotated, List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model import GameScrapeDetail
from enums import ScrapeStatus


class GameScrapeDetailRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_details(self) -> List[GameScrapeDetail]:
        query = select(GameScrapeDetail)
        result = await self.session.scalars(query)
        return list(result.all())

    async def get_detail_by_id(self, detail_id: UUID) -> Optional[GameScrapeDetail]:
        query = select(GameScrapeDetail).where(GameScrapeDetail.id == detail_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_details_by_request_id(
        self, request_id: UUID
    ) -> List[GameScrapeDetail]:
        query = select(GameScrapeDetail).where(
            GameScrapeDetail.scrape_request_id == request_id
        )
        result = await self.session.scalars(query)
        return list(result.all())

    async def get_details_by_scraped_data_id(
        self, scraped_data_id: UUID
    ) -> List[GameScrapeDetail]:
        query = select(GameScrapeDetail).where(
            GameScrapeDetail.scraped_game_data_id == scraped_data_id
        )
        result = await self.session.scalars(query)
        return list(result.all())

    async def get_details_by_status(
        self, request_id: UUID, status: ScrapeStatus
    ) -> List[GameScrapeDetail]:
        query = select(GameScrapeDetail).where(
            GameScrapeDetail.scrape_request_id == request_id,
            GameScrapeDetail.status == status,
        )
        result = await self.session.scalars(query)
        return list(result.all())

    async def create_detail(self, detail_data: GameScrapeDetail) -> GameScrapeDetail:
        query = (
            insert(GameScrapeDetail)
            .values(
                id=detail_data.id,
                scrape_request_id=detail_data.scrape_request_id,
                scraped_game_data_id=detail_data.scraped_game_data_id,
                status=detail_data.status,
                error_message=detail_data.error_message,
                raw_data=detail_data.raw_data,
            )
            .returning(GameScrapeDetail)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_detail(
        self, detail_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[GameScrapeDetail]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        query = (
            update(GameScrapeDetail)
            .where(GameScrapeDetail.id == detail_id)
            .values(**update_data)
            .returning(GameScrapeDetail)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete_detail(self, detail_id: UUID) -> bool:
        query = (
            delete(GameScrapeDetail)
            .where(GameScrapeDetail.id == detail_id)
            .returning(GameScrapeDetail.id)
        )
        result = await self.session.execute(query)
    
        return bool(result.scalar_one_or_none())


GameScrapeDetailRepositoryDependency = Annotated[
    GameScrapeDetailRepository, Depends(GameScrapeDetailRepository)
]
