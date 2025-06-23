from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field

class GameDTO(BaseModel):
    id: UUID = Field(..., description="ID of the game")
    name: str = Field(..., description="Name of the game")
    description: Optional[str] = Field(None, description="Description of the game")
    metadata_json: Optional[dict] = Field(None, description="Metadata of the game")

    class Config:
        from_attributes = True


class CreateGameDTO(BaseModel):
    name: str = Field(..., description="Name of the game")
    description: Optional[str] = Field(None, description="Description of the game")
    metadata_json: Optional[dict] = Field(None, description="Metadata of the game")
