from uuid import UUID
from sqlalchemy import Uuid, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from model.base import Base


class RegressionResults(Base):
    __tablename__ = "regression_results"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, index=True)
    request_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_requests.id", ondelete="CASCADE"),
        nullable=False,
    )

    coefficients_json: Mapped[str] = mapped_column(JSON, nullable=False)
    std_errors_json: Mapped[str] = mapped_column(JSON, nullable=False)
    t_statistics_json: Mapped[str] = mapped_column(JSON, nullable=False)
    p_values_json: Mapped[str] = mapped_column(JSON, nullable=False)

    r_squared: Mapped[float] = mapped_column(Float, nullable=False)
    adj_r_squared: Mapped[float] = mapped_column(Float, nullable=False)
    f_statistic: Mapped[float] = mapped_column(Float, nullable=False)
    f_p_value: Mapped[float] = mapped_column(Float, nullable=False)
    n_observations: Mapped[int] = mapped_column(Integer, nullable=False)

    request = relationship("AnalysisRequests", back_populates="results")
