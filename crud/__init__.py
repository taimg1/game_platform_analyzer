from crud.game_repository import GameRepositoryDependency
from crud.platform_repository import PlatformRepositoryDependency
from crud.scraped_game_data_repository import ScrapedGameDataRepositoryDependency
from crud.scrape_request_repository import ScrapeRequestRepositoryDependency
from crud.scrape_result_repository import ScrapeResultRepositoryDependency
from crud.game_scrape_detail_repository import GameScrapeDetailRepositoryDependency
from crud.analysis_requests_repository import AnalysisRequestsRepositoryDependency
from crud.regression_results_repository import RegressionResultsRepositoryDependency


__all__ = [
    "GameRepositoryDependency",
    "PlatformRepositoryDependency",
    "ScrapedGameDataRepositoryDependency",
    "ScrapeRequestRepositoryDependency",
    "ScrapeResultRepositoryDependency",
    "GameScrapeDetailRepositoryDependency", 
    "AnalysisRequestsRepositoryDependency",
    "RegressionResultsRepositoryDependency",
]

