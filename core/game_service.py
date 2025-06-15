from uuid import UUID
import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from crud import GameRepositoryDependency
from schemas import CreateGameDTO, GameDTO
from model import Game
from typing import Annotated
from fastapi import Depends


class GameService:
    def __init__(self, game_repo: GameRepositoryDependency):
        self.game_repo = game_repo

    async def get_all_games(self):
        return [GameDTO.from_orm(game) for game in await self.game_repo.get_all_games()]

    async def get_game_by_id(self, game_id: UUID):
        game = await self.game_repo.get_game_by_id(game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with id {game_id} not found",
            )
        return GameDTO.from_orm(game)

    async def get_game_by_name(self, game_name: str):
        game = await self.game_repo.get_game_by_name(game_name)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with name '{game_name}' not found",
            )
        return GameDTO.from_orm(game)

    async def create_game(self, game_data: CreateGameDTO):
        game_to_create = Game(
            id=uuid.uuid4(),
            name=game_data.name,
            description=game_data.description,  
            metadata_json=game_data.metadata_json,
        )
        try:
            created_game = await self.game_repo.create_game(game_to_create)
            if not created_game:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create game record before commit.",
                )
            return GameDTO.from_orm(created_game)
        except IntegrityError as e:
            if (
                e.orig
                and "UNIQUE constraint failed" in str(e.orig).lower()
                and "games.name" in str(e.orig).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Game with name '{game_data.name}' already exists.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data integrity error: {str(e.orig) or str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}",
            )

    async def update_game(self, game_dto: GameDTO):
        existing_game = await self.game_repo.get_game_by_id(game_dto.id)
        if not existing_game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with id {game_dto.id} not found for update",
            )

        game_model_to_update = Game(
            id=game_dto.id,
            name=game_dto.name,
            description=game_dto.description,
            metadata_json=game_dto.metadata_json,
        )
        try:
            updated_game_result = await self.game_repo.update_game(game_model_to_update)
            if not updated_game_result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update game with id {game_dto.id} after repository call.",
                )
            return GameDTO.from_orm(updated_game_result)
        except IntegrityError as e:
            if (
                e.orig
                and "UNIQUE constraint failed" in str(e.orig).lower()
                and "games.name" in str(e.orig).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Game name '{game_dto.name}' already exists for another game.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data integrity error during update: {str(e.orig) or str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during update: {str(e)}",
            )

    async def delete_game(self, game_id: UUID):
        game_to_delete = await self.game_repo.get_game_by_id(game_id)
        if not game_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with id {game_id} not found for deletion",
            )

        deleted_game = await self.game_repo.delete_game(game_id)
        if not deleted_game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game with id {game_id} could not be deleted or was already deleted.",
            )
        return GameDTO.from_orm(deleted_game)


GameServiceDependency = Annotated[GameService, Depends(GameService)]
