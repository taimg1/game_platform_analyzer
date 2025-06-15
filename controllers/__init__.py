from controllers.platform_controller import router as platform_router
from controllers.game_controller import router as game_router
from controllers.game_scrape_controller import router as game_scrape_router

__all__ = [
    "platform_router",
    "game_router",
    "game_scrape_router",
]
