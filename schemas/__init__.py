from .game_schemas import GameDTO, CreateGameDTO
from .platform_schemas import PlatformDTO, CreatePlatformDTO
from .scraped_game_data_schemas import ScrapedGameDataDTO, CreateScrapedGameDataDTO, ScrapeRequest

__all__ = [
    "GameDTO",
    "CreateGameDTO",
    "PlatformDTO",
    "CreatePlatformDTO",
    "ScrapedGameDataDTO",
    "CreateScrapedGameDataDTO",
    "ScrapeRequest",
]