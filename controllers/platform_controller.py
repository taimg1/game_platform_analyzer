from typing import List
from uuid import UUID

from fastapi import APIRouter, status

from core import PlatformServiceDependency
from schemas import PlatformDTO, CreatePlatformDTO

router = APIRouter(
    prefix="/platforms",
    tags=["Platforms"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request"},
        status.HTTP_200_OK: {"description": "Success"},
        status.HTTP_201_CREATED: {"description": "Created"},
        status.HTTP_204_NO_CONTENT: {"description": "No content"},
    },
)


@router.post("/", response_model=PlatformDTO, status_code=status.HTTP_201_CREATED)
async def create_platform(
    platform_data: CreatePlatformDTO, service: PlatformServiceDependency
):
    return await service.create_platform(platform_data)


@router.get("/", response_model=List[PlatformDTO])
async def get_all_platforms(service: PlatformServiceDependency):
    return await service.get_all_platforms()


@router.get("/{platform_id}", response_model=PlatformDTO)
async def get_platform_by_id(platform_id: UUID, service: PlatformServiceDependency):
    return await service.get_platform_by_id(platform_id)


@router.get("/name/{platform_name}", response_model=PlatformDTO)
async def get_platform_by_name(platform_name: str, service: PlatformServiceDependency):
    return await service.get_platform_by_name(platform_name)


@router.put("/{platform_id}", response_model=PlatformDTO)
async def update_platform(
    platform_id: UUID,
    platform_data: CreatePlatformDTO,
    service: PlatformServiceDependency,
):
    platform_to_update = PlatformDTO(
        id=platform_id,
        name=platform_data.name,
        search_url_template=platform_data.search_url_template,
        base_url=platform_data.base_url,
        game_data_selector=platform_data.game_data_selector,
    )
    return await service.update_platform(platform_to_update)


@router.delete("/{platform_id}", response_model=PlatformDTO)
async def delete_platform(platform_id: UUID, service: PlatformServiceDependency):
    return await service.delete_platform(platform_id)
