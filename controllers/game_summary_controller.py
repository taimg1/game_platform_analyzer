import io
from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

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


@router.get("/", response_class=StreamingResponse)
async def generate_game_summary(
    game_id: UUID, service: GameSummaryServiceDependency
) -> StreamingResponse:
    pdf_bytes, file_name = await service.generate_summary_pdf_for_game(game_id)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={file_name}",
        },
    )
