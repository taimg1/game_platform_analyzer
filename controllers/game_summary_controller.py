from fastapi import APIRouter, status
from uuid import UUID
from typing import Dict, Any

from core import GameSummaryServiceDependency

router = APIRouter(
    prefix="/games/{game_id}/summary",
    tags=["Game Summary"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Game or scraped data not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
    },
)


@router.get("/", response_model=Dict[str, Any])
async def generate_game_summary(
    game_id: UUID, service: GameSummaryServiceDependency
) -> Dict[str, Any]:
    file_info = await service.generate_summary_pdf_for_game(game_id)
    return {"file": file_info}
