from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model.regression_results import RegressionResults


class RegressionResultsRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_results(self):
        query = select(RegressionResults)
        result = await self.session.scalars(query)
        return result.all()

    async def get_result_by_id(self, result_id: UUID):
        query = select(RegressionResults).where(RegressionResults.id == result_id)
        result = await self.session.scalars(query)
        return result.first()

    async def get_results_by_request_id(self, request_id: UUID):
        query = select(RegressionResults).where(
            RegressionResults.request_id == request_id
        )
        result = await self.session.scalars(query)
        return result.all()

    async def create_result(self, result: RegressionResults) -> RegressionResults:
        query = insert(RegressionResults).values(
            id=result.id,
            request_id=result.request_id,
            coefficients_json=result.coefficients_json,
            std_errors_json=result.std_errors_json,
            t_statistics_json=result.t_statistics_json,
            p_values_json=result.p_values_json,
            r_squared=result.r_squared,
            adj_r_squared=result.adj_r_squared,
            f_statistic=result.f_statistic,
            f_p_value=result.f_p_value,
            n_observations=result.n_observations,
        )
        await self.session.execute(query)
        await self.session.commit()
        return result

    async def update_result(self, result: RegressionResults) -> RegressionResults:
        query = (
            update(RegressionResults)
            .where(RegressionResults.id == result.id)
            .values(
                coefficients_json=result.coefficients_json,
                std_errors_json=result.std_errors_json,
                t_statistics_json=result.t_statistics_json,
                p_values_json=result.p_values_json,
                r_squared=result.r_squared,
                adj_r_squared=result.adj_r_squared,
                f_statistic=result.f_statistic,
                f_p_value=result.f_p_value,
                n_observations=result.n_observations,
            )
        )
        await self.session.execute(query)
        await self.session.commit()
        return result

    async def delete_result(self, result_id: UUID):
        query = delete(RegressionResults).where(RegressionResults.id == result_id)
        await self.session.execute(query)
        await self.session.commit()
        return result_id


RegressionResultsRepositoryDependency = Annotated[
    RegressionResultsRepository, Depends(RegressionResultsRepository)
]
