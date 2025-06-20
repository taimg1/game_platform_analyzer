from model.base import Base
from model.platform import Platform
from model.game import Game
from model.scraped_game_data import ScrapedGameData
from model.game_scrape_detail import GameScrapeDetail
from model.scrape_request import ScrapeRequest
from model.scrape_result import ScrapeResult
from model.analysis_requests import AnalysisRequests
from model.regression_results import RegressionResults


__all__ = [
    "Base",
    "Platform",
    "Game",
    "ScrapedGameData",
    "GameScrapeDetail",
    "ScrapeRequest",
    "ScrapeResult",
    "AnalysisRequests",
    "RegressionResults",
]
