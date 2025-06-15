from uuid import UUID
import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from crud import (
    GameRepositoryDependency,
    PlatformRepositoryDependency,
    ScrapedGameDataRepositoryDependency,
)
from model import Game, ScrapedGameData, Platform
from schemas import ScrapedGameDataDTO
from untils import WebScraperDependency
from enums import GameStatusEnum
from typing import Annotated
from fastapi import Depends


class GameScrapeService:
    def __init__(
        self,
        game_repo: GameRepositoryDependency,
        scraped_data_repo: ScrapedGameDataRepositoryDependency,
        platform_repo: PlatformRepositoryDependency,
        web_scraper: WebScraperDependency,
    ):
        self.game_repo = game_repo
        self.scraped_data_repo = scraped_data_repo
        self.platform_repo = platform_repo
        self.web_scraper = web_scraper

    async def scrape_games_for_platform(
        self, platform_id: UUID, limit: int = 10
    ) -> list[ScrapedGameDataDTO]:
        platform: Platform = await self.platform_repo.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with id {platform_id} not found for scraping.",
            )

        game_urls = await self.web_scraper.collect_game_urls(
            platform.search_url_template, limit
        )

        scraped_results: list[ScrapedGameDataDTO] = []

        for url in game_urls:
            data = await self.web_scraper.extract_game_data_from_url(url)
            if not data or not data.get("name"):
                continue

            game = await self.game_repo.get_game_by_name(data["name"])
            if not game:
                try:
                    game_to_create = Game(
                        id=uuid.uuid4(),
                        name=data["name"],
                        description=data.get("description"),
                        metadata_json=self.web_scraper.clean_json(
                            data.get("metadata_json", {})
                        ),
                    )
                    game = await self.game_repo.create_game(game_to_create)
                    if not game:
                        continue
                except IntegrityError:
                    game = await self.game_repo.get_game_by_name(data["name"])
                    if not game:
                        continue
                except Exception as e:
                    print("Failed to create game:", e)
                    continue

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

            try:
                result = await self.scraped_data_repo.create_scraped_data(scraped_game)
                scraped_results.append(ScrapedGameDataDTO.model_validate(result))
            except IntegrityError as e:
                print('Fail with', e)
                continue
            except Exception as e:
                print("Failed to create scraped game data:", e)
                continue

        return scraped_results


GameScrapeServiceDependency = Annotated[GameScrapeService, Depends(GameScrapeService)]
