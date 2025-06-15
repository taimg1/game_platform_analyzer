from fastapi import APIRouter, status

from core import GameScrapeServiceDependency
from schemas import ScrapeRequest

router = APIRouter(
    prefix="/scrape",
    tags=["Scraping"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_202_ACCEPTED: {"description": "Accepted"},
    },
)


@router.post("/scrape", status_code=status.HTTP_202_ACCEPTED)
async def scrape_games_for_platform_endpoint(
    request: ScrapeRequest,
    service: GameScrapeServiceDependency,
):
    result = await service.scrape_games_for_platform(request.platform_id, request.limit)
    return {
        "message": f"Scraping initiated for platform {request.platform_id} with limit {request.limit}.",
        "result": result,
    }
