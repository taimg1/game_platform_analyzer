from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class AnalysisRequestDto(BaseModel):
    """DTO for retrieving an analysis request."""

    id: UUID = Field(..., description="ID of the analysis request")
    created_at: datetime = Field(..., description="Creation timestamp")
    csv_filename: str = Field(..., description="CSV filename")
    dependent_variable: str = Field(..., description="Dependent variable")
    independent_variables: List[str] = Field(..., description="Independent variables")
    formula: Optional[str] = Field(None, description="Formula")

    model_config = ConfigDict(
        from_attributes=True,
    )


class AnalysisRequestCreateDto(BaseModel):
    """DTO for creating a new analysis request."""

    dependent_variable: str = Field(..., description="Dependent variable")
    independent_variables: List[str] = Field(..., description="Independent variables")


class AnalysisRequestConfigDto(BaseModel):
    """DTO for validating the configuration object submitted by the user."""

    dependent_variable: str = Field(..., description="Dependent variable")
    independent_variables: List[str] = Field(..., description="Independent variables")


class RegressionResultDto(BaseModel):
    """DTO for retrieving regression results."""

    id: UUID = Field(..., description="ID of the regression result")
    request_id: UUID = Field(..., description="ID of the analysis request")
    coefficients_json: Dict[str, float] = Field(..., description="Coefficients JSON")
    std_errors_json: Dict[str, float] = Field(..., description="Standard errors JSON")
    t_statistics_json: Dict[str, float] = Field(..., description="T-statistics JSON")
    p_values_json: Dict[str, float] = Field(..., description="P-values JSON")
    r_squared: float = Field(..., description="R-squared value")
    adj_r_squared: float = Field(..., description="Adjusted R-squared value")
    f_statistic: float = Field(..., description="F-statistic value")
    f_p_value: float = Field(..., description="F-p-value value")
    n_observations: int = Field(..., description="Number of observations")

    model_config = ConfigDict(
        from_attributes=True,
    )


class RegressionResultCreateDto(BaseModel):
    """DTO for creating a new regression result."""

    request_id: UUID = Field(..., description="ID of the analysis request")
    coefficients_json: Dict[str, float] = Field(..., description="Coefficients JSON")
    std_errors_json: Dict[str, float] = Field(..., description="Standard errors JSON")
    t_statistics_json: Dict[str, float] = Field(..., description="T-statistics JSON")
    p_values_json: Dict[str, float] = Field(..., description="P-values JSON")
    r_squared: float = Field(..., description="R-squared value")
    adj_r_squared: float = Field(..., description="Adjusted R-squared value")
    f_statistic: float = Field(..., description="F-statistic value")
    f_p_value: float = Field(..., description="F-p-value value")
    n_observations: int = Field(..., description="Number of observations")


class RegressionResultResponseDto(BaseModel):
    """DTO for the API response with analysis results."""

    analysis_id: UUID = Field(..., description="ID of the analysis request")
    model_summary: Dict[str, Any] = Field(..., description="Model summary")