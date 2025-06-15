from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model import Platform


class PlatformRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_platforms(self):
        query = select(Platform)
        result = await self.session.scalars(query)
        return result.all()

    async def get_platform_by_id(self, platform_id: UUID):
        query = select(Platform).where(Platform.id == platform_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_platform_by_name(self, platform_name: str):
        query = select(Platform).where(Platform.name == platform_name)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def create_platform(self, platform: Platform):
        query = (
            insert(Platform)
            .values(
                id=platform.id,
                name=platform.name,
                search_url_template=platform.search_url_template,
                base_url=platform.base_url,
                game_data_selector=platform.game_data_selector,
            )
            .returning(Platform)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_platform(self, platform: Platform):
        query = (
            update(Platform)
            .where(Platform.id == platform.id)
            .values(**platform.dict())
            .returning(Platform)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete_platform(self, platform_id: UUID):
        query = delete(Platform).where(Platform.id == platform_id).returning(Platform)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()


PlatformRepositoryDependency = Annotated[
    PlatformRepository, Depends(PlatformRepository)
]
