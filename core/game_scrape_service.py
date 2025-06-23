import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from crud import (
    GameRepositoryDependency,
    PlatformRepositoryDependency,
    ScrapedGameDataRepositoryDependency,
    ScrapeRequestRepositoryDependency,
    ScrapeResultRepositoryDependency,
    GameScrapeDetailRepositoryDependency,
)
from enums import GameStatusEnum, ScrapeRequestStatus, ScrapeStatus
from model import (
    Game,
    Platform,
    ScrapedGameData,
    ScrapeRequest,
    ScrapeResult,
    GameScrapeDetail,
)
from schemas import ScrapedGameDataDTO, GameScrapeDetailDTO, ScrapeRequestDTO
from untils import WebScraperDependency
from typing import Annotated


class GameScrapeService:
    def __init__(
        self,
        game_repo: GameRepositoryDependency,
        scraped_data_repo: ScrapedGameDataRepositoryDependency,
        platform_repo: PlatformRepositoryDependency,
        scrape_request_repo: ScrapeRequestRepositoryDependency,
        scrape_result_repo: ScrapeResultRepositoryDependency,
        game_scrape_detail_repo: GameScrapeDetailRepositoryDependency,
        web_scraper: WebScraperDependency,
    ):
        self.game_repo = game_repo
        self.scraped_data_repo = scraped_data_repo
        self.platform_repo = platform_repo
        self.scrape_request_repo = scrape_request_repo
        self.scrape_result_repo = scrape_result_repo
        self.game_scrape_detail_repo = game_scrape_detail_repo
        self.web_scraper = web_scraper

    async def scrape_games_for_platform(
        self, platform_id: UUID, limit: int = 10
    ) -> ScrapeRequestDTO:
        platform: Platform = await self.platform_repo.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with id {platform_id} not found for scraping.",
            )

        scrape_request = ScrapeRequest(
            id=uuid.uuid4(),
            platform_id=platform_id,
            status=ScrapeRequestStatus.PENDING,
            total_games=0,
        )
        created_request = await self.scrape_request_repo.create_request(scrape_request)

        request_id = created_request.id
        error_message = None
        processed_games = 0
        successful_scrapes = 0
        failed_scrapes = 0
        scraped_games = []
        scrape_details_list = []
        scrape_result = None

        try:
            await self.scrape_request_repo.update_request(
                request_id,
                {
                    "status": ScrapeRequestStatus.IN_PROGRESS,
                    "started_at": datetime.now(timezone.utc),
                },
            )

            game_urls = await self.web_scraper.collect_game_urls(
                platform.search_url_template, limit
            )

            await self.scrape_request_repo.update_request(
                request_id, {"total_games": len(game_urls)}
            )

            not_found = 0
            for url in game_urls:
                scraped_data_id = None
                detail_status = ScrapeStatus.PENDING
                detail_error = None
                game_name = "Unknown"
                raw_data = None

                try:
                    data = await self.web_scraper.extract_game_data_from_url(url)
                    raw_data = data
                    if not data or not data.get("name"):
                        not_found += 1
                        detail_status = ScrapeStatus.NOT_FOUND
                        detail_error = "Game name not found on page."
                        raise ValueError(detail_error)

                    game_name = data["name"]

                    game = await self.game_repo.get_game_by_name(game_name)
                    if not game:
                        try:
                            game_to_create = Game(
                                id=uuid.uuid4(),
                                name=game_name,
                                description=data.get("description"),
                                metadata_json=self.web_scraper.clean_json(
                                    data.get("metadata_json", {})
                                ),
                            )
                            game = await self.game_repo.create_game(game_to_create)
                        except IntegrityError:
                            game = await self.game_repo.get_game_by_name(game_name)

                    if not game:
                        raise Exception(f"Failed to create or find game: {game_name}")

                    scraped_game = ScrapedGameData(
                        id=uuid.uuid4(),
                        name_on_platform=data["name"],
                        price=data["price"],
                        price_in_usd=data["price_in_usd"],
                        currency=data["currency"],
                        availability_status=GameStatusEnum(data["availability_status"]),
                        url_on_platform=data["url_on_platform"],
                        rating=data.get("rating"),
                        reviews_count=data.get("reviews_count"),
                        search_position=data.get("search_position"),
                        special_content_json=data.get("special_content_json"),
                        discount_info_json=self.web_scraper.clean_json(
                            data.get("discount_info_json")
                        ),
                        game_id=game.id,
                        platform_id=platform.id,
                    )

                    result = await self.scraped_data_repo.create_scraped_data(
                        scraped_game
                    )
                    if not result:
                        raise Exception("Failed to save scraped data to the database.")
                    scraped_games.append(ScrapedGameDataDTO.model_validate(result))

                    scraped_data_id = result.id
                    successful_scrapes += 1
                    detail_status = ScrapeStatus.SUCCESS

                except Exception as e:
                    failed_scrapes += 1
                    detail_status = ScrapeStatus.FAILURE
                    detail_error = str(e)

                finally:
                    detail = GameScrapeDetail(
                        id=uuid.uuid4(),
                        scrape_request_id=request_id,
                        scraped_game_data_id=scraped_data_id,
                        status=detail_status,
                        error_message=detail_error,
                        raw_data=raw_data,
                    )
                    created_detail = await self.game_scrape_detail_repo.create_detail(
                        detail
                    )
                    if created_detail:
                        scrape_details_list.append(
                            GameScrapeDetailDTO.model_validate(created_detail)
                        )
                    processed_games += 1

            scrape_result = ScrapeResult(
                id=uuid.uuid4(),
                scrape_request_id=request_id,
                platform_id=platform_id,
                total_games=len(game_urls),
                successful_scrapes=successful_scrapes,
                failed_scrapes=failed_scrapes,
                not_found=not_found,
                started_at=created_request.created_at,
                completed_at=datetime.now(timezone.utc),
            )
            await self.scrape_result_repo.create_result(scrape_result)

        except Exception as e:
            error_message = str(e)
            print(f"Scraping failed for request {request_id}: {e}")

        finally:
            final_status = (
                ScrapeRequestStatus.FAILED
                if error_message
                else ScrapeRequestStatus.COMPLETED
            )
            final_update = {
                "status": final_status,
                "completed_at": datetime.now(timezone.utc),
                "processed_games": processed_games,
                "successful_scrapes": successful_scrapes,
                "failed_scrapes": failed_scrapes,
                "error_message": error_message,
            }
            updated_request = await self.scrape_request_repo.update_request(
                request_id, final_update
            )
            response_dto = ScrapeRequestDTO.model_validate(updated_request)
            response_dto.results = scraped_games
            response_dto.scrape_details = scrape_details_list
            return response_dto


GameScrapeServiceDependency = Annotated[GameScrapeService, Depends(GameScrapeService)]
