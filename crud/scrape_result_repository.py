from typing import Annotated, List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model import ScrapeResult


class ScrapeResultRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_results(self) -> List[ScrapeResult]:
        query = select(ScrapeResult)
        result = await self.session.scalars(query)
        return list(result.all())

    async def get_result_by_id(self, result_id: UUID) -> Optional[ScrapeResult]:
        query = select(ScrapeResult).where(ScrapeResult.id == result_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_result_by_request_id(
        self, request_id: UUID
    ) -> Optional[ScrapeResult]:
        query = select(ScrapeResult).where(ScrapeResult.scrape_request_id == request_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_results_by_platform_id(self, platform_id: UUID) -> List[ScrapeResult]:
        query = select(ScrapeResult).where(ScrapeResult.platform_id == platform_id)
        result = await self.session.scalars(query)
        return list(result.all())

    async def create_result(self, result_data: ScrapeResult) -> ScrapeResult:
        query = (
            insert(ScrapeResult)
            .values(
                id=result_data.id,
                scrape_request_id=result_data.scrape_request_id,
                platform_id=result_data.platform_id,
                total_games=result_data.total_games,
                successful_scrapes=result_data.successful_scrapes,
                failed_scrapes=result_data.failed_scrapes,
                not_found=result_data.not_found,
                started_at=result_data.started_at,
                completed_at=result_data.completed_at,
                scrape_metadata=result_data.scrape_metadata,
            )
            .returning(ScrapeResult)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_result(
        self, result_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[ScrapeResult]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        query = (
            update(ScrapeResult)
            .where(ScrapeResult.id == result_id)
            .values(**update_data)
            .returning(ScrapeResult)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete_result(self, result_id: UUID) -> bool:
        query = (
            delete(ScrapeResult)
            .where(ScrapeResult.id == result_id)
            .returning(ScrapeResult.id)
        )
        result = await self.session.execute(query)

        return bool(result.scalar_one_or_none())


ScrapeResultRepositoryDependency = Annotated[
    ScrapeResultRepository, Depends(ScrapeResultRepository)
]
