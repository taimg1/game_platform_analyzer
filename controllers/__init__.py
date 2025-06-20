from controllers.platform_controller import router as platform_router
from controllers.game_controller import router as game_router
from controllers.game_scrape_controller import router as game_scrape_router
from controllers.analysis_controller import router as analysis_router
from controllers.game_summary_controller import router as game_summary_router

__all__ = [
    "platform_router",
    "game_router",
    "game_scrape_router",
    "analysis_router",
    "game_summary_router",
]
