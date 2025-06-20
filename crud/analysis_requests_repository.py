from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, insert, update, delete

from db import SessionLocalDependency
from model.analysis_requests import AnalysisRequests


class AnalysisRequestsRepository:
    def __init__(self, session: SessionLocalDependency):
        self.session = session

    async def get_all_requests(self):
        query = select(AnalysisRequests)
        result = await self.session.scalars(query)

        return result.all()

    async def get_request_by_id(self, request_id: UUID):
        query = select(AnalysisRequests).where(AnalysisRequests.id == request_id)
        result = await self.session.scalars(query)
        return result.first()

    async def create_request(self, request: AnalysisRequests):
        query = insert(AnalysisRequests).values(
            id=request.id,
            created_at=request.created_at,
            csv_filename=request.csv_filename,
            dependent_variable=request.dependent_variable,
            independent_variables=request.independent_variables,
            formula=request.formula,
        )
        result = await self.session.execute(query)
        return result

    async def update_request(self, request: AnalysisRequests):
        query = (
            update(AnalysisRequests)
            .where(AnalysisRequests.id == request.id)
            .values(
                csv_filename=request.csv_filename,
                dependent_variable=request.dependent_variable,
                independent_variables=request.independent_variables,
                formula=request.formula,
            )
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result

    async def delete_request(self, request_id: UUID):
        query = delete(AnalysisRequests).where(AnalysisRequests.id == request_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result


AnalysisRequestsRepositoryDependency = Annotated[
    AnalysisRequestsRepository, Depends(AnalysisRequestsRepository)
]
