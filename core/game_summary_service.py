from typing import Annotated
from fastapi import Depends, HTTPException
from uuid import UUID

from crud.game_repository import GameRepositoryDependency
from untils.gemini_api import GeminiApiDependency


class GameSummaryService:
    def __init__(
        self,
        game_repo: GameRepositoryDependency,
        gemini_api: GeminiApiDependency,
    ):
        self.game_repo = game_repo
        self.gemini_api = gemini_api

    async def generate_summary_pdf_for_game(self, game_id: UUID) -> dict:
        game = await self.game_repo.get_game_by_id(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")

        scraped_data = await self.game_repo.get_game_scraped_data_with_platforms(
            game_id
        )
        if not scraped_data:
            raise HTTPException(status_code=404, detail="No scraped data found")

        stats = []
        for rec in scraped_data:
            stats.append(
                {
                    "platform": rec.platform.name if rec.platform else "Unknown",
                    "price": rec.price_in_usd,
                    "availability": rec.availability_status.value,
                    "rating": rec.rating,
                    "discount": rec.discount_info_json,
                }
            )

        prompt = (
            f"You are a professional market analyst. Given the following JSON array of stats for the game '{game.name}' "
            f"across multiple platforms, generate a professionally formatted PDF report. The report should include sections: "
            f"Summary, Pricing, Ratings, Discount, and Conclusion. Format it for export as a PDF document.\n\n"
            f"Return the PDF using file_output tool with the filename '{game.name.replace(' ', '_')}_Market_Analysis.pdf'.\n"
            f"\nHere is the input JSON:\n```json\n{stats}\n```"
        )

        file_info = await self.gemini_api.generate_file_from_prompt(prompt)
        if not file_info:
            raise HTTPException(
                status_code=500, detail="Failed to generate PDF file via Gemini"
            )

        return file_info


GameSummaryServiceDependency = Annotated[
    GameSummaryService, Depends(GameSummaryService)
]
