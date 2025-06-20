from fastapi import APIRouter

from core.analysis_service import AnalysisServiceDependency
from schemas.regression_schemas import (
    AnalysisRequestCreateDto,
    RegressionResultResponseDto,
)


router = APIRouter(
    prefix="/analysis",
    tags=["analysis"],
)


@router.post("/custom", response_model=RegressionResultResponseDto)
async def perform_custom_analysis(
    analysis_service: AnalysisServiceDependency,
    analysis_config: AnalysisRequestCreateDto,
) -> RegressionResultResponseDto:
    return await analysis_service.perform_analysis(analysis_config)


@router.post("/price-vs-genre-publisher", response_model=RegressionResultResponseDto)
async def perform_price_vs_genre_publisher_analysis(
    analysis_service: AnalysisServiceDependency,
) -> RegressionResultResponseDto:
    analysis_config = AnalysisRequestCreateDto(
        dependent_variable="price_in_usd", independent_variables=["genre", "publisher"]
    )
    return await analysis_service.perform_analysis(analysis_config)


@router.post("/price-vs-rating", response_model=RegressionResultResponseDto)
async def perform_price_vs_rating_analysis(
    analysis_service: AnalysisServiceDependency,
) -> RegressionResultResponseDto:
    analysis_config = AnalysisRequestCreateDto(
        dependent_variable="price_in_usd", independent_variables=["rating"]
    )
    return await analysis_service.perform_analysis(analysis_config)


@router.post(
    "/languages-vs-genre-platform-publisher", response_model=RegressionResultResponseDto
)
async def perform_languages_vs_genre_platform_publisher_analysis(
    analysis_service: AnalysisServiceDependency,
) -> RegressionResultResponseDto:
    analysis_config = AnalysisRequestCreateDto(
        dependent_variable="n_text_languages",
        independent_variables=["genre", "platform_id", "publisher"],
    )
    return await analysis_service.perform_analysis(analysis_config)
