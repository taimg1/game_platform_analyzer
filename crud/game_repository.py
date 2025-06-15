from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model import Game


class GameRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_games(self):
        query = select(Game)
        result = await self.session.scalars(query)
        return result.all()

    async def get_game_by_id(self, game_id: UUID):
        query = select(Game).where(Game.id == game_id)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def get_game_by_name(self, game_name: str):
        query = select(Game).where(Game.name == game_name)
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def create_game(self, game: Game):
        query = (
            insert(Game)
            .values(
                id=game.id,
                name=game.name,
                description=game.description,
                metadata_json=game.metadata_json,
            )
            .returning(Game)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def update_game(self, game: Game):
        query = (
            update(Game)
            .where(Game.id == game.id)
            .values(
                id=game.id,
                name=game.name,
                description=game.description,
                metadata_json=game.metadata_json,
            )
            .returning(Game)
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def delete_game(self, game_id: UUID):
        query = delete(Game).where(Game.id == game_id).returning(Game)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()


GameRepositoryDependency = Annotated[GameRepository, Depends(GameRepository)]
