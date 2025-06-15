from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class GameDTO(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    metadata_json: Optional[dict]

    class Config:
        from_attributes = True


class CreateGameDTO(BaseModel):
    name: str
    description: Optional[str]
    metadata_json: Optional[dict]
