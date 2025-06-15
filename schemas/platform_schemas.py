from uuid import UUID
from pydantic import BaseModel

class PlatformDTO(BaseModel):
    id: UUID
    name: str
    base_url: str
    search_url_template: str
    game_data_selector: str

    class Config:
        from_attributes = True
        


class CreatePlatformDTO(BaseModel):
    name: str
    base_url: str
    search_url_template: str
    game_data_selector: str
