
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import platform_controller, game_controller, game_scrape_controller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(platform_controller.router)
app.include_router(game_controller.router)
app.include_router(game_scrape_controller.router)

