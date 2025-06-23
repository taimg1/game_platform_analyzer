from typing import Annotated
from uuid import uuid4
from datetime import datetime, timezone
import pandas as pd

from fastapi import Depends, HTTPException

from crud import (
    ScrapedGameDataRepositoryDependency,
    AnalysisRequestsRepositoryDependency,
    RegressionResultsRepositoryDependency,
)
from model import AnalysisRequests, RegressionResults
from schemas import (
    AnalysisRequestCreateDto,
    RegressionResultResponseDto,
)
from untils import RegressionModel, GeminiApiDependency


class AnalysisService:
    def __init__(
        self,
        scraped_data_repo: ScrapedGameDataRepositoryDependency,
        analysis_requests_repo: AnalysisRequestsRepositoryDependency,
        regression_results_repo: RegressionResultsRepositoryDependency,
        gemini_api: GeminiApiDependency,
    ):
        self.scraped_data_repo = scraped_data_repo
        self.analysis_requests_repo = analysis_requests_repo
        self.regression_results_repo = regression_results_repo
        self.gemini_api = gemini_api

    def extract_features_locally(self, rec) -> dict:
        try:
            metadata = rec.game.metadata_json or {}
            discount = rec.discount_info_json or {}
            genres = metadata.get("genres", [])
            features = metadata.get("features", [])
            languages = metadata.get("languages_supported", {}).get("text", [])
            release_date = metadata.get("release_date")
            discounted_price = discount.get("discounted_price", 0)
            original_price = discount.get("original_price", rec.price_in_usd)

            days_since_release = None
            if release_date:
                try:
                    date_obj = datetime.fromisoformat(release_date)
                    days_since_release = (datetime.now(timezone.utc) - date_obj).days
                except Exception:
                    pass

            return {
                "num_genres": len(genres),
                "main_genre": genres[0] if genres else None,
                "num_features": len(features),
                "has_discount": int(discounted_price > 0),
                "discount_pct": (
                    round((original_price - discounted_price) / original_price * 100, 2)
                    if original_price and discounted_price
                    else 0
                ),
                "days_since_release": days_since_release,
                "n_text_languages": len(languages),
            }
        except Exception:
            return {
                "num_genres": 0,
                "main_genre": None,
                "num_features": 0,
                "has_discount": False,
                "discount_pct": 0,
                "days_since_release": None,
                "n_text_languages": 0,
            }

    async def perform_analysis(
        self, config: AnalysisRequestCreateDto
    ) -> RegressionResultResponseDto:
        try:
            scraped_records = list(await self.scraped_data_repo.get_all_scraped_data())
            if not scraped_records:
                raise HTTPException(404, "No scraped data found to analyze.")

            reg_model = RegressionModel(scraped_records)
            base_df = reg_model.df
            extra_features = [
                self.extract_features_locally(rec) for rec in scraped_records
            ]
            extra_df = pd.DataFrame(extra_features)
            combined_df = pd.concat([base_df.reset_index(drop=True), extra_df], axis=1)

            reg_model.df = combined_df
            results = reg_model.run_regression(
                config.dependent_variable,
                config.independent_variables,
            )
            formula = f"{config.dependent_variable} ~ {' + '.join(config.independent_variables)}"
            analysis_request = AnalysisRequests(
                id=uuid4(),
                created_at=datetime.now(timezone.utc),
                csv_filename="database",
                dependent_variable=config.dependent_variable,
                independent_variables=config.independent_variables,
                formula=formula,
            )
            await self.analysis_requests_repo.create_request(analysis_request)

            regression_result = RegressionResults(
                id=uuid4(),
                request_id=analysis_request.id,
                coefficients_json=results["coefficients"],
                std_errors_json=results["std_errors"],
                t_statistics_json=results["t_statistics"],
                p_values_json=results["p_values"],
                r_squared=results["r_squared"],
                adj_r_squared=results["adj_r_squared"],
                f_statistic=results["f_statistic"],
                f_p_value=results["f_p_value"],
                n_observations=results["n_observations"],
            )
            await self.regression_results_repo.create_result(regression_result)

            return RegressionResultResponseDto(
                analysis_id=analysis_request.id,
                model_summary=results,
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal error: {e}")


AnalysisServiceDependency = Annotated[AnalysisService, Depends(AnalysisService)]
