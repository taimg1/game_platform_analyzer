from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model import ScrapedGameData


class ScrapedGameDataRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_scraped_data(self):
        query = select(ScrapedGameData)
        result = await self.session.scalars(query)
        return result.all()

    async def get_scraped_data_by_id(self, scraped_data_id: UUID):
        query = select(ScrapedGameData).where(ScrapedGameData.id == scraped_data_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_scraped_data_by_game_id(self, game_id: UUID):
        query = select(ScrapedGameData).where(ScrapedGameData.game_id == game_id)
        result = await self.session.scalars(query)
        return result.all()

    async def get_scraped_data_by_platform_id(self, platform_id: UUID):
        query = select(ScrapedGameData).where(
            ScrapedGameData.platform_id == platform_id
        )
        result = await self.session.scalars(query)
        return result.all()

    async def create_scraped_data(self, scraped_data: ScrapedGameData):
        query = (
            insert(ScrapedGameData)
            .values(
                id=scraped_data.id,
                game_id=scraped_data.game_id,
                platform_id=scraped_data.platform_id,
                name_on_platform=scraped_data.name_on_platform,
                price=scraped_data.price,
                price_in_usd=scraped_data.price_in_usd,
                currency=scraped_data.currency,
                availability_status=scraped_data.availability_status,
                url_on_platform=scraped_data.url_on_platform,
                rating=scraped_data.rating,
                reviews_count=scraped_data.reviews_count,
                search_position=scraped_data.search_position,
                special_content_json=scraped_data.special_content_json,
                discount_info_json=scraped_data.discount_info_json,
            )
            .returning(ScrapedGameData)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_scraped_data(self, scraped_data: ScrapedGameData):
        query = (
            update(ScrapedGameData)
            .where(ScrapedGameData.id == scraped_data.id)
            .values(
                game_id=scraped_data.game_id,
                platform_id=scraped_data.platform_id,
                name_on_platform=scraped_data.name_on_platform,
                price=scraped_data.price,
                price_in_usd=scraped_data.price_in_usd,
                currency=scraped_data.currency,
                availability_status=scraped_data.availability_status,
                url_on_platform=scraped_data.url_on_platform,
                rating=scraped_data.rating,
                reviews_count=scraped_data.reviews_count,
                search_position=scraped_data.search_position,
                special_content_json=scraped_data.special_content_json,
                discount_info_json=scraped_data.discount_info_json,
            )
            .returning(ScrapedGameData)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete_scraped_data(self, scraped_data_id: UUID):
        query = (
            delete(ScrapedGameData)
            .where(ScrapedGameData.id == scraped_data_id)
            .returning(ScrapedGameData)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()


ScrapedGameDataRepositoryDependency = Annotated[
    ScrapedGameDataRepository, Depends(ScrapedGameDataRepository)
]
