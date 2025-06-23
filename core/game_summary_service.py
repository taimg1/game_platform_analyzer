import json
from typing import Annotated, Tuple
from uuid import UUID

from fastapi import Depends, HTTPException

from crud import GameRepositoryDependency
from untils import GeminiApiDependency, PdfReportServiceDependency

class GameSummaryService:
    def __init__(
        self,
        game_repo: GameRepositoryDependency,
        gemini_api: GeminiApiDependency,
        pdf_report_service: PdfReportServiceDependency,
    ):
        self.game_repo = game_repo
        self.gemini_api = gemini_api
        self.pdf_report_service = pdf_report_service

    async def generate_summary_pdf_for_game(self, game_id: UUID) -> Tuple[bytes, str]:
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
            f"across multiple platforms, generate a detailed analysis. "
            f"The output MUST be a single JSON object with the following keys: "
            f"'summary', 'pricing_analysis', 'rating_analysis', 'discount_analysis', 'conclusion'.\n\n"
            f"Here is the input JSON:\n```json\n{stats}\n```\n\n"
            f"Respond ONLY with the JSON object, without any markdown formatting."
        )

        try:
            summary_text = await self.gemini_api.generate_response(prompt) or ""
            cleared_summary_text = self.gemini_api.clean_json_markdown(summary_text)

            summary_data = json.loads(cleared_summary_text)

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500, detail="Failed to parse summary data from Gemini"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate summary from Gemini: {e}"
            )

        if not summary_data:
            raise HTTPException(
                status_code=500, detail="Failed to generate summary data via Gemini"
            )

        file_name = f"{game.name.replace(' ', '_')}_Market_Analysis.pdf"
        pdf_bytes = self.pdf_report_service.generate_game_summary_report(
            game.name, summary_data
        )

        return pdf_bytes, file_name


GameSummaryServiceDependency = Annotated[
    GameSummaryService, Depends(GameSummaryService)
]
