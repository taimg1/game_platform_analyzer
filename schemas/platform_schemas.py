from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.networks import HttpUrl

class PlatformDTO(BaseModel):
    id: UUID
    name: str = Field(description="Name of the platform")
    base_url: HttpUrl = Field(description="Base URL of the platform")
    search_url_template: HttpUrl = Field(description="Search URL template of the platform")
    game_data_selector: str = Field(description="Game data selector of the platform")

    class Config:
        from_attributes = True
        


class CreatePlatformDTO(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    base_url: HttpUrl = Field(max_length=255)
    search_url_template: HttpUrl = Field(max_length=255)
    game_data_selector: str = Field(max_length=255)
