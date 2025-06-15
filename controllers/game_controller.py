from typing import List
from uuid import UUID

from fastapi import APIRouter, status
from schemas import GameDTO, CreateGameDTO
from core import GameServiceDependency


router = APIRouter(
    prefix="/games",
    tags=["Games"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_201_CREATED: {"description": "Created"},
        status.HTTP_204_NO_CONTENT: {"description": "No content"},
    },
)


@router.get("/", response_model=List[GameDTO])
async def get_all_games(game_service: GameServiceDependency):
    return await game_service.get_all_games()


@router.get("/{game_id}", response_model=GameDTO)
async def get_game_by_id(game_id: UUID, game_service: GameServiceDependency):
    return await game_service.get_game_by_id(game_id)


@router.get("/name/{game_name}", response_model=GameDTO)
async def get_game_by_name(game_name: str, game_service: GameServiceDependency):
    return await game_service.get_game_by_name(game_name)


@router.post("/", response_model=GameDTO)
async def create_game(game: CreateGameDTO, game_service: GameServiceDependency):
    return await game_service.create_game(game)


@router.put("/{game_id}", response_model=GameDTO)
async def update_game(
    game_id: UUID, game_data: CreateGameDTO, game_service: GameServiceDependency
):
    game_to_update = GameDTO(id=game_id, **game_data.model_dump())
    return await game_service.update_game(game_to_update)


@router.delete("/{game_id}", response_model=GameDTO)
async def delete_game(game_id: UUID, game_service: GameServiceDependency):
    return await game_service.delete_game(game_id)
