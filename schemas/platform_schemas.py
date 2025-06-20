from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.networks import HttpUrl

class PlatformDTO(BaseModel):
    id: UUID
    name: str = Field(
        max_length=100, 
        min_length=2, 
    )
    base_url: HttpUrl = Field(max_length=255, min_length=5)
    search_url_template: HttpUrl = Field(max_length=255, min_length=5)
    game_data_selector: str = Field(max_length=255, min_length=5)

    class Config:
        from_attributes = True
        


class CreatePlatformDTO(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    base_url: HttpUrl = Field(max_length=255, min_length=5)
    search_url_template: HttpUrl = Field(max_length=255, min_length=5)
    game_data_selector: str = Field(max_length=255, min_length=5)
