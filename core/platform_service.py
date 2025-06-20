from uuid import UUID
import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from crud import PlatformRepositoryDependency
from schemas import CreatePlatformDTO, PlatformDTO
from model import Platform
from typing import Annotated
from fastapi import Depends


class PlatformService:
    def __init__(self, platform_repo: PlatformRepositoryDependency):
        self.platform_repo = platform_repo

    async def get_all_platforms(self):
        platforms = await self.platform_repo.get_all_platforms()
        return [PlatformDTO.from_orm(platform) for platform in platforms]

    async def get_platform_by_id(self, platform_id: UUID):
        platform = await self.platform_repo.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with id {platform_id} not found",
            )
        return PlatformDTO.from_orm(platform)

    async def get_platform_by_name(self, platform_name: str):
        platform = await self.platform_repo.get_platform_by_name(platform_name)
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with name '{platform_name}' not found",
            )
        return PlatformDTO.from_orm(platform)

    async def create_platform(self, platform_data: CreatePlatformDTO):
        platform_to_create = Platform(
            id=uuid.uuid4(),
            name=platform_data.name,
            search_url_template=str(platform_data.search_url_template),
            base_url=str(platform_data.base_url),
            game_data_selector=str(platform_data.game_data_selector),
        )
        try:
            created_platform = await self.platform_repo.create_platform(
                platform_to_create
            )
            if not created_platform:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create platform record.",
                )
            return PlatformDTO.from_orm(created_platform)
        except IntegrityError as e:
            if (
                e.orig
                and "UNIQUE constraint failed" in str(e.orig).lower()
                and "platforms.name" in str(e.orig).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Platform with name '{platform_data.name}' already exists.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data integrity error: {str(e.orig) or str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}",
            )

    async def update_platform(self, platform_dto: PlatformDTO):
        existing_platform = await self.platform_repo.get_platform_by_id(platform_dto.id)
        if not existing_platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with id {platform_dto.id} not found for update",
            )

        platform_model_to_update = Platform(
            id=platform_dto.id,
            name=platform_dto.name,
            search_url_template=str(platform_dto.search_url_template),
            base_url=str(platform_dto.base_url),
            game_data_selector=str(platform_dto.game_data_selector),
        )
        try:
            updated_platform_result = await self.platform_repo.update_platform(
                platform_model_to_update
            )
            if not updated_platform_result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update platform with id {platform_dto.id}.",
                )
            return PlatformDTO.from_orm(updated_platform_result)
        except IntegrityError as e:
            if (
                e.orig
                and "UNIQUE constraint failed" in str(e.orig).lower()
                and "platforms.name" in str(e.orig).lower()
            ):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Platform name '{platform_dto.name}' already exists for another platform.",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Data integrity error during update: {str(e.orig) or str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during update: {str(e)}",
            )

    async def delete_platform(self, platform_id: UUID):
        platform_to_delete = await self.platform_repo.get_platform_by_id(platform_id)
        if not platform_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform with id {platform_id} not found for deletion",
            )
        try:
            deleted_platform = await self.platform_repo.delete_platform(platform_id)
            if not deleted_platform:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Platform with id {platform_id} could not be deleted or was already deleted.",
                )
            return PlatformDTO.from_orm(deleted_platform)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while deleting platform {platform_id}: {str(e)}",
            )


PlatformServiceDependency = Annotated[PlatformService, Depends(PlatformService)]
