from typing import Annotated, List, Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model import ScrapeRequest
from enums import ScrapeRequestStatus


class ScrapeRequestRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_requests(self) -> List[ScrapeRequest]:
        query = select(ScrapeRequest)
        result = await self.session.scalars(query)
        return list(result.all())

    async def get_request_by_id(self, request_id: UUID) -> Optional[ScrapeRequest]:
        query = select(ScrapeRequest).where(ScrapeRequest.id == request_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_requests_by_platform_id(
        self, platform_id: UUID
    ) -> List[ScrapeRequest]:
        query = select(ScrapeRequest).where(ScrapeRequest.platform_id == platform_id)
        result = await self.session.scalars(query)
        return list(result.all())

    async def get_requests_by_status(
        self, status: ScrapeRequestStatus
    ) -> List[ScrapeRequest]:
        query = select(ScrapeRequest).where(ScrapeRequest.status == status)
        result = await self.session.scalars(query)
        return list(result.all())

    async def create_request(self, request_data: ScrapeRequest) -> ScrapeRequest:
        query = (
            insert(ScrapeRequest)
            .values(
                id=request_data.id,
                platform_id=request_data.platform_id,
                status=request_data.status,
                started_at=request_data.started_at,
                completed_at=request_data.completed_at,
                error_message=request_data.error_message,
            )
            .returning(ScrapeRequest)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_request(
        self, request_id: UUID, update_data: dict
    ) -> Optional[ScrapeRequest]:
        update_data["updated_at"] = datetime.now(timezone.utc)
        query = (
            update(ScrapeRequest)
            .where(ScrapeRequest.id == request_id)
            .values(**update_data)
            .returning(ScrapeRequest)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete_request(self, request_id: UUID) -> bool:
        query = (
            delete(ScrapeRequest)
            .where(ScrapeRequest.id == request_id)
            .returning(ScrapeRequest.id)
        )
        result = await self.session.execute(query)

        return bool(result.scalar_one_or_none())


ScrapeRequestRepositoryDependency = Annotated[
    ScrapeRequestRepository, Depends(ScrapeRequestRepository)
]
