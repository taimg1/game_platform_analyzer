from fastapi import APIRouter, status

from core import GameScrapeServiceDependency
from schemas import ScrapeGamesRequest, ScrapeRequestDTO

router = APIRouter(
    prefix="/scrape",
    tags=["Scraping"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
    },
)


@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=ScrapeRequestDTO)
async def scrape_games_for_platform_endpoint(
    request: ScrapeGamesRequest,
    service: GameScrapeServiceDependency,
) -> ScrapeRequestDTO:
    scrape_request = await service.scrape_games_for_platform(
        request.platform_id, request.limit
    )
    return scrape_request
